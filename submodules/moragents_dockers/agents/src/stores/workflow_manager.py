import json
import logging
from typing import Dict, Optional, List, Any
from pathlib import Path
import asyncio
import aiofiles
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from src.agents.dca_agent.tools import DCAActionHandler

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Status states for workflows"""

    ACTIVE = "active"  # Workflow is active and will be executed on schedule
    PAUSED = "paused"  # Workflow is temporarily paused but can be resumed
    COMPLETED = "completed"  # Workflow has finished successfully
    FAILED = "failed"  # Workflow encountered an error and stopped
    CANCELLED = "cancelled"  # Workflow was manually cancelled


@dataclass
class Workflow:
    """
    Represents a scheduled recurring action workflow.

    A workflow defines an automated task that runs on a schedule. It contains all the
    information needed to execute an action periodically, track its progress, and
    manage its lifecycle.

    Attributes:
        id (str): Unique identifier for the workflow
        name (str): Human-readable name for the workflow
        description (str): Detailed description of what the workflow does
        action (str): Name of the action to execute (e.g. "dca_trade")
        params (Dict[str, Any]): Parameters required by the action
        interval (timedelta): Time between workflow executions
        last_run (Optional[datetime]): When the workflow last executed
        next_run (Optional[datetime]): When the workflow will next execute
        status (WorkflowStatus): Current status of the workflow
        created_at (datetime): When the workflow was created
        updated_at (datetime): When the workflow was last modified
        metadata (Dict): Additional workflow metadata

    Methods:
        to_dict(): Serializes workflow to dictionary format
        from_dict(): Creates workflow instance from dictionary data
    """

    id: str
    name: str
    description: str
    action: str
    params: Dict[str, Any]
    interval: timedelta
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert workflow to dictionary format for storage.

        Returns:
            dict: Dictionary representation of the workflow with all attributes
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "params": self.params,
            "interval": self.interval.total_seconds(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        """
        Create workflow instance from dictionary data.

        Args:
            data (dict): Dictionary containing workflow data

        Returns:
            Workflow: New workflow instance initialized with the provided data
        """
        workflow = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            action=data["action"],
            params=data["params"],
            interval=timedelta(seconds=data["interval"]),
            status=WorkflowStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )
        if data.get("last_run"):
            workflow.last_run = datetime.fromisoformat(data["last_run"])
        if data.get("next_run"):
            workflow.next_run = datetime.fromisoformat(data["next_run"])
        return workflow


class WorkflowManager:
    """
    Manages the lifecycle and execution of automated workflows.

    The WorkflowManager handles creation, scheduling, execution, and persistence of
    workflows. It provides a robust system for running recurring automated tasks with
    proper error handling, state management, and data persistence.

    Key Features:
        - Asynchronous workflow execution
        - Persistent storage of workflow data
        - Configurable action handlers
        - Automatic scheduling and execution
        - Thread-safe operations with locking
        - Comprehensive error handling and logging

    Attributes:
        storage_path (Path): Path to workflow storage file
        workflows (Dict[str, Workflow]): In-memory store of active workflows
        _lock (asyncio.Lock): Lock for thread-safe operations
        _scheduler_task (Optional[asyncio.Task]): Background scheduler task
        _action_handlers (Dict[str, Any]): Registered workflow action handlers

    Example Usage:
        manager = WorkflowManager()
        await manager.initialize()

        # Create a new workflow
        workflow = await manager.create_workflow(
            name="DCA Bitcoin",
            description="Weekly BTC purchase",
            action="dca_trade",
            params={"amount": 100, "asset": "BTC"},
            interval=timedelta(days=7)
        )

        # List active workflows
        workflows = await manager.list_workflows()

        # Update workflow
        await manager.update_workflow(workflow.id, status=WorkflowStatus.PAUSED)

        # Delete workflow
        await manager.delete_workflow(workflow.id)
    """

    def __init__(self, storage_path: str = "workflows.json"):
        """Initialize the WorkflowManager"""
        self.storage_path = Path(storage_path)
        self.workflows: Dict[str, Workflow] = {}
        self._lock = asyncio.Lock()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._action_handlers: Dict[str, Any] = {}

        # Register DCA action handler by default
        self.register_action_handler("dca_trade", DCAActionHandler())

    def register_action_handler(self, action_name: str, handler: Any) -> None:
        """Register a handler for a workflow action"""
        self._action_handlers[action_name] = handler

    async def initialize(self) -> None:
        """Initialize storage and load existing workflows"""
        try:
            if not self.storage_path.exists():
                await self._save_workflows({})
            await self._load_workflows()
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("Workflow manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize workflow manager: {e}")
            raise

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks and executes due workflows"""
        while True:
            try:
                logger.info("Workflow scheduler checking for due workflows...")
                now = datetime.now()
                active_workflows = [w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE]
                logger.info(f"Found {len(active_workflows)} active workflows")

                for workflow in self.workflows.values():
                    logger.info(f"Checking workflow {workflow.id} ({workflow.name})")
                    if workflow.status == WorkflowStatus.ACTIVE and workflow.next_run and now >= workflow.next_run:
                        logger.info(f"Executing workflow {workflow.id} ({workflow.name})")
                        await self._execute_workflow(workflow)

                # Sleep for a short interval before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error

    async def _execute_workflow(self, workflow: Workflow) -> None:
        """Execute a single workflow action"""
        try:
            if workflow.action not in self._action_handlers:
                raise ValueError(f"No handler registered for action: {workflow.action}")

            handler = self._action_handlers[workflow.action]
            await handler.execute(workflow.params)

            # Update workflow timing
            workflow.last_run = datetime.now()
            workflow.next_run = workflow.last_run + workflow.interval
            workflow.updated_at = datetime.now()

            # Check if we should keep or remove the workflow
            should_remove = False

            # Check if total investment amount is reached (for DCA workflows)
            if workflow.action == "dca_trade" and "total_investment_amount" in workflow.params:
                total_invested = workflow.params.get("total_invested", 0)
                total_target = float(workflow.params["total_investment_amount"])
                step_size = float(workflow.params["step_size"])

                # Update total invested amount
                total_invested += step_size
                workflow.params["total_invested"] = total_invested

                # Check if we've reached the target
                if total_invested >= total_target:
                    workflow.status = WorkflowStatus.COMPLETED
                    should_remove = True
                    logger.info(f"Workflow {workflow.id} completed - reached total investment target")

            # Remove completed/failed workflows, keep active ones
            if should_remove:
                del self.workflows[workflow.id]

            await self._save_workflows(self._workflows_to_dict())
            logger.info(f"Successfully executed workflow {workflow.id}")

        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow.id}: {e}")
            workflow.status = WorkflowStatus.FAILED
            await self._save_workflows(self._workflows_to_dict())

    async def create_workflow(
        self,
        name: str,
        description: str,
        action: str,
        params: Dict[str, Any],
        interval: timedelta,
        metadata: Dict = None,
    ) -> Workflow:
        """Create a new workflow"""
        try:
            workflow_id = f"wf_{int(datetime.now().timestamp())}"
            now = datetime.now()
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                action=action,
                params=params,
                interval=interval,
                next_run=now + interval,
                metadata=metadata or {},
            )

            async with self._lock:
                self.workflows[workflow_id] = workflow
                await self._save_workflows(self._workflows_to_dict())

            logger.info(f"Created new workflow: {workflow_id}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)

    async def update_workflow(self, workflow_id: str, **updates) -> Optional[Workflow]:
        """Update workflow properties"""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                logger.warning(f"Workflow not found: {workflow_id}")
                return None

            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)

            workflow.updated_at = datetime.now()

            async with self._lock:
                await self._save_workflows(self._workflows_to_dict())

            logger.info(f"Updated workflow: {workflow_id}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to update workflow: {e}")
            raise

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            if workflow_id not in self.workflows:
                return False

            async with self._lock:
                del self.workflows[workflow_id]
                await self._save_workflows(self._workflows_to_dict())

            logger.info(f"Deleted workflow: {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            raise

    async def list_workflows(self) -> List[Workflow]:
        """Get list of all workflows"""
        return list(self.workflows.values())

    def _workflows_to_dict(self) -> Dict:
        """Convert workflows to dictionary format for storage"""
        return {workflow_id: workflow.to_dict() for workflow_id, workflow in self.workflows.items()}

    async def _save_workflows(self, data: Dict) -> None:
        """Save workflows to storage file"""
        try:
            async with aiofiles.open(self.storage_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save workflows: {e}")
            raise

    async def _load_workflows(self) -> None:
        """Load workflows from storage file"""
        try:
            async with aiofiles.open(self.storage_path, "r") as f:
                content = await f.read()
                data = json.loads(content)
                self.workflows = {
                    workflow_id: Workflow.from_dict(workflow_data) for workflow_id, workflow_data in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load workflows: {e}")
            raise


# Create singleton instance
workflow_manager_instance = WorkflowManager()
