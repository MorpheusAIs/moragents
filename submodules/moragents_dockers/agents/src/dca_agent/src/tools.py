from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Callable, Union

logger = logging.getLogger(__name__)

class DCAError(Exception):
    """Base exception for DCA operations"""
    pass

class StrategyError:
    """Strategy-related error hierarchy"""
    class NotFound(DCAError):
        """Strategy not found"""
        pass

    class ValidationFailed(DCAError):
        """Strategy validation failed"""
        pass

    class ExecutionFailed(DCAError):
        """Strategy execution failed"""
        pass

class HealthStatus(str, Enum):
    """Health status enum for strategies"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    PENDING = "pending"
    INACTIVE = "inactive"

T = TypeVar('T')

# Configuration constants
CONFIG = {
    "health": {
        "warning_threshold": 1.5,  # 150% of interval
        "critical_threshold": 2.0,  # 200% of interval
    },
    "cleanup": {
        "retention_days": 30
    },
    "execution": {
        "liquidity_threshold": Decimal("1000"),
        "gas_buffer": Decimal("1.02"),  # 2% buffer
        "max_retries": 3,
        "retry_delay": 1  # seconds
    }
}

class IntervalType(str, Enum):
    """Interval types for DCA strategies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class DCAConfig:
    token_address: str
    amount: Decimal
    interval_seconds: int
    total_periods: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    max_slippage: Decimal = Decimal("0.01")  # 1%
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None


# Add missing handlers
async def handle_get_status(strategy_id: str, include_history: bool = False) -> Dict[str, Any]:
    """Handler for getting strategy status"""
    try:
        store = JsonFileStrategyStore()
        strategy = store.load(strategy_id)
        
        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")
            
        response = {
            "id": strategy.id,
            "status": strategy.status.value,
            "current_period": strategy.current_period,
            "last_execution": strategy.last_execution.isoformat() if strategy.last_execution else None,
            "next_execution": strategy.next_execution.isoformat() if strategy.next_execution else None,
            "metrics": strategy.calculate_metrics().to_dict(),
            "config": strategy.config.to_dict()
        }
        
        if include_history:
            response["history"] = strategy.history
            response["status_history"] = strategy.metadata.get("status_history", [])
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting strategy status: {str(e)}")
        return {"error": str(e)}

async def handle_pause_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for pausing DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = store.load(strategy_id)
        
        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")
            
        result = strategy.pause()
        if result.success:
            store.save(strategy)
            
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error pausing strategy: {str(e)}")
        return {"error": str(e)}

async def handle_resume_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for resuming DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = store.load(strategy_id)
        
        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")
            
        result = strategy.resume()
        if result.success:
            store.save(strategy)
            
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error resuming strategy: {str(e)}")
        return {"error": str(e)}

async def handle_cancel_dca(strategy_id: str) -> Dict[str, Any]:
    """Handler for cancelling DCA strategy"""
    try:
        store = JsonFileStrategyStore()
        strategy = store.load(strategy_id)
        
        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")
            
        result = strategy.cancel()
        if result.success:
            store.save(strategy)
            
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error cancelling strategy: {str(e)}")
        return {"error": str(e)}

async def handle_create_dca(
    token_address: str,
    amount: str,
    interval: str,
    total_periods: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    max_slippage: float = 1.0,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    time_limit: Optional[int] = None
) -> Dict[str, Any]:
    """Handler for creating new DCA strategy"""
    try:
        # Create strategy configuration
        config_data = {
            "token_address": token_address,
            "amount": amount,
            "interval": interval,
            "total_periods": total_periods,
            "min_price": min_price,
            "max_price": max_price,
            "max_slippage": max_slippage / 100,  # Convert percentage to decimal
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "time_limit": time_limit
        }
        
        # Create and validate strategy
        strategy = Strategy.create_new(**config_data)
        
        # Save strategy
        store = JsonFileStrategyStore()
        store.save(strategy)
        
        return {
            "success": True,
            "message": "Strategy created successfully",
            "strategy_id": strategy.id,
            "initial_config": strategy.config.to_dict(),
            "next_execution": strategy.next_execution.isoformat() if strategy.next_execution else None
        }
        
    except Exception as e:
        logger.error(f"Error creating DCA strategy: {str(e)}")
        return {"error": str(e)}

async def handle_check_health(strategy_id: str) -> Dict[str, Any]:
    """Handler for checking strategy health"""
    try:
        store = JsonFileStrategyStore()
        strategy = store.load(strategy_id)
        
        if not strategy:
            raise StrategyError.NotFound(f"Strategy {strategy_id} not found")
            
        health_status = strategy.check_health()
        metrics = strategy.calculate_metrics()
        
        response = {
            "status": health_status.value,
            "strategy_id": strategy_id,
            "current_status": strategy.status.value,
            "last_execution": strategy.last_execution.isoformat() if strategy.last_execution else None,
            "next_execution": strategy.next_execution.isoformat() if strategy.next_execution else None,
            "error_count": strategy.metadata.get("error_count", 0),
            "metrics": metrics.to_dict(),
            "warnings": []
        }
        
        # Add relevant warnings
        if health_status == HealthStatus.WARNING:
            response["warnings"].append("Strategy execution is delayed")
        elif health_status == HealthStatus.CRITICAL:
            response["warnings"].append("Strategy execution is critically delayed")
            
        if metrics.failed_txs > 0:
            response["warnings"].append(f"Strategy has {metrics.failed_txs} failed transactions")
            
        return response
        
    except Exception as e:
        logger.error(f"Error checking strategy health: {str(e)}")
        return {"error": str(e)}
    
def get_tools() -> List[Dict[str, Any]]:
    """Get tool definitions for LLM function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "set_cdp_credentials",
                "description": "Set Coinbase Developer Platform API credentials",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cdpApiKey": {
                            "type": "string",
                            "description": "CDP API Key"
                        },
                        "cdpApiSecret": {
                            "type": "string",
                            "description": "CDP API Secret"
                        }
                    },
                    "required": ["cdpApiKey", "cdpApiSecret"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_dollar_cost_average",
                "description": "Create a new dollar cost averaging strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token_address": {
                            "type": "string",
                            "description": "Address of token to DCA into"
                        },
                        "amount": {
                            "type": "string",
                            "description": "Amount to invest per period"
                        },
                        "interval": {
                            "type": "string",
                            "enum": [e.value for e in IntervalType],
                            "description": "Time between purchases"
                        },
                        "total_periods": {
                            "type": "integer",
                            "description": "Optional number of periods to run"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Optional minimum price to execute purchase"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Optional maximum price to execute purchase"
                        },
                        "max_slippage": {
                            "type": "number",
                            "description": "Maximum acceptable slippage percentage (default 1%)",
                            "default": 1.0
                        },
                        "stop_loss": {
                            "type": "number",
                            "description": "Optional stop loss price"
                        },
                        "take_profit": {
                            "type": "number",
                            "description": "Optional take profit price"
                        }
                    },
                    "required": ["token_address", "amount", "interval"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_pause_dca",
                "description": "Pause an active DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to pause"
                        }
                    },
                    "required": ["strategy_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_resume_dca",
                "description": "Resume a paused DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to resume"
                        }
                    },
                    "required": ["strategy_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_cancel_dca",
                "description": "Cancel a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to cancel"
                        }
                    },
                    "required": ["strategy_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_get_status",
                "description": "Get current status and metrics of a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy"
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include execution history in response",
                            "default": False
                        }
                    },
                    "required": ["strategy_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_check_health",
                "description": "Check health status of a DCA strategy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {
                            "type": "string",
                            "description": "ID of the DCA strategy to check"
                        }
                    },
                    "required": ["strategy_id"]
                }
            }
        }
    ]

class StrategyStatus(str, Enum):
    """Strategy execution status with transition rules"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

    @property
    def is_terminal(self) -> bool:
        return self in {self.COMPLETED, self.CANCELLED, self.ERROR}

    @property
    def allowed_transitions(self) -> set:
        """Define valid status transitions"""
        transitions = {
            self.ACTIVE: {self.PAUSED, self.CANCELLED, self.COMPLETED, self.ERROR},
            self.PAUSED: {self.ACTIVE, self.CANCELLED},
            self.COMPLETED: set(),
            self.CANCELLED: set(),
            self.ERROR: {self.ACTIVE, self.CANCELLED}
        }
        return transitions[self]

@dataclass
class ExecutionResult:
    """Encapsulates strategy execution results"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.error:
            result["error"] = self.error
        else:
            result.update(self.data)
        return result

@dataclass
class StrategyMetrics:
    """Strategy performance metrics"""
    total_periods: int
    successful_txs: int
    failed_txs: int
    total_invested: Decimal
    avg_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    roi: Optional[Decimal] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_periods": self.total_periods,
            "successful_transactions": self.successful_txs,
            "failed_transactions": self.failed_txs,
            "total_invested": str(self.total_invested),
            **({"average_price": str(self.avg_price)} if self.avg_price else {}),
            **({"minimum_price": str(self.min_price)} if self.min_price else {}),
            **({"maximum_price": str(self.max_price)} if self.max_price else {}),
            **({"return_on_investment": str(self.roi)} if self.roi else {})
        }

@dataclass
class Strategy:
    """Enhanced DCA strategy implementation"""
    id: str
    config: DCAConfig
    status: StrategyStatus = field(default=StrategyStatus.ACTIVE)
    current_period: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize strategy metadata"""
        self.metadata.setdefault("status_history", [])
        self.metadata.setdefault("creation_time", datetime.now().isoformat())

    async def execute(self, client: Any) -> ExecutionResult:
        """Execute strategy purchase"""
        if self.status != StrategyStatus.ACTIVE:
            return ExecutionResult(
                success=False,
                error=f"Strategy {self.id} is not active (current status: {self.status})"
            )

        try:
            # Get current price
            price = await self._get_token_price(client)
            
            # Check execution conditions
            if not self._should_execute(price):
                return ExecutionResult(
                    success=True,
                    data={
                        "status": "skipped",
                        "reason": "Execution conditions not met",
                        "price": str(price)
                    }
                )

            # Execute transaction
            result = await self._execute_transaction(client, price)
            self._update_execution_state(price, result.transaction_hash)
            
            return ExecutionResult(
                success=True,
                data={
                    "status": "success",
                    "transaction_hash": result.transaction_hash,
                    "price": str(price),
                    "amount": str(self.config.amount),
                    "next_execution": self.next_execution.isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}", exc_info=True)
            self._handle_execution_error(e)
            return ExecutionResult(success=False, error=str(e))

    def pause(self) -> ExecutionResult:
        """Pause strategy execution"""
        try:
            if self.status != StrategyStatus.ACTIVE:
                return ExecutionResult(
                    success=False,
                    error=f"Cannot pause strategy in {self.status} status"
                )

            self._transition_to(StrategyStatus.PAUSED, "User requested pause")
            self.metadata["paused_at"] = datetime.now().isoformat()

            return ExecutionResult(
                success=True,
                data={
                    "status": "paused",
                    "paused_at": self.metadata["paused_at"],
                    "current_period": self.current_period
                }
            )
        except Exception as e:
            logger.error(f"Failed to pause strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def resume(self) -> ExecutionResult:
        """Resume paused strategy"""
        try:
            if self.status != StrategyStatus.PAUSED:
                return ExecutionResult(
                    success=False,
                    error=f"Cannot resume strategy in {self.status} status"
                )

            self._transition_to(StrategyStatus.ACTIVE, "User requested resume")
            self._calculate_next_execution()
            self.metadata["resumed_at"] = datetime.now().isoformat()

            return ExecutionResult(
                success=True,
                data={
                    "status": "active",
                    "resumed_at": self.metadata["resumed_at"],
                    "next_execution": self.next_execution.isoformat() if self.next_execution else None
                }
            )
        except Exception as e:
            logger.error(f"Failed to resume strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def cancel(self) -> ExecutionResult:
        """Cancel strategy execution"""
        try:
            if self.status.is_terminal:
                return ExecutionResult(
                    success=False,
                    error=f"Cannot cancel strategy in {self.status} status"
                )

            previous_status = self.status
            self._transition_to(StrategyStatus.CANCELLED, "User requested cancellation")
            
            metrics = self.calculate_metrics()
            self.metadata.update({
                "cancelled_at": datetime.now().isoformat(),
                "final_metrics": metrics.to_dict(),
                "previous_status": previous_status.value
            })

            return ExecutionResult(
                success=True,
                data={
                    "status": "cancelled",
                    "cancelled_at": self.metadata["cancelled_at"],
                    "metrics": metrics.to_dict()
                }
            )
        except Exception as e:
            logger.error(f"Failed to cancel strategy: {str(e)}")
            return ExecutionResult(success=False, error=str(e))

    def calculate_metrics(self) -> StrategyMetrics:
        """Calculate current strategy metrics"""
        successful_txs = [tx for tx in self.history if tx.get("status") == "success"]
        failed_txs = [tx for tx in self.history if tx.get("status") == "failed"]
        
        total_invested = sum(Decimal(tx["amount"]) for tx in successful_txs)
        
        metrics = StrategyMetrics(
            total_periods=self.current_period,
            successful_txs=len(successful_txs),
            failed_txs=len(failed_txs),
            total_invested=total_invested
        )
        
        if successful_txs:
            prices = [Decimal(tx["price"]) for tx in successful_txs]
            metrics.avg_price = sum(prices) / len(prices)
            metrics.min_price = min(prices)
            metrics.max_price = max(prices)
            
            # Calculate ROI if possible
            if self.config.token_address in self.metadata.get("current_prices", {}):
                current_value = (
                    total_invested * 
                    Decimal(str(self.metadata["current_prices"][self.config.token_address]))
                )
                metrics.roi = ((current_value - total_invested) / total_invested * 100
                             ).quantize(Decimal("0.01"))
        
        return metrics

    def _transition_to(self, new_status: StrategyStatus, reason: str) -> None:
        """Handle status transitions with validation"""
        if new_status not in self.status.allowed_transitions:
            raise StrategyError.ValidationFailed(
                f"Invalid transition from {self.status} to {new_status}"
            )

        old_status = self.status
        self.status = new_status
        
        # Record transition in history
        self.metadata["status_history"].append({
            "timestamp": datetime.now().isoformat(),
            "old_status": old_status.value,
            "new_status": new_status.value,
            "reason": reason
        })

    def _calculate_next_execution(self) -> None:
        """Calculate next execution time"""
        if self.last_execution:
            self.next_execution = (
                self.last_execution + 
                timedelta(seconds=self.config.interval.seconds)
            )
        else:
            self.next_execution = datetime.now() + timedelta(
                seconds=self.config.interval.seconds
            )

    def _should_execute(self, price: Decimal) -> bool:
        """Check if execution conditions are met"""
        price_in_range = (
            (self.config.min_price is None or price >= self.config.min_price) and
            (self.config.max_price is None or price <= self.config.max_price)
        )
        
        if not price_in_range:
            logger.info(f"Price {price} outside bounds for strategy {self.id}")
            return False
            
        if self.config.total_periods and self.current_period >= self.config.total_periods:
            logger.info(f"Strategy {self.id} reached total periods limit")
            self._transition_to(StrategyStatus.COMPLETED, "Total periods reached")
            return False
            
        return True

    async def _execute_transaction(self, client: Any, price: Decimal) -> Any:
        """Execute token swap transaction"""
        # Calculate minimum tokens with slippage protection
        min_tokens = (
            self.config.amount / 
            price * 
            (1 - self.config.max_slippage)
        ).quantize(Decimal("0.00000001"))

        # Check stop loss and take profit
        if self.config.stop_loss and price <= self.config.stop_loss:
            self._transition_to(
                StrategyStatus.COMPLETED, 
                f"Stop loss triggered at price {price}"
            )
            return None

        if self.config.take_profit and price >= self.config.take_profit:
            self._transition_to(
                StrategyStatus.COMPLETED, 
                f"Take profit triggered at price {price}"
            )
            return None

        # Execute swap with retry logic
        for attempt in range(CONFIG["execution"]["max_retries"]):
            try:
                tx = await client.swap(
                    amount=str(self.config.amount),
                    token_address=self.config.token_address,
                    min_tokens=str(min_tokens),
                    slippage_tolerance=float(self.config.max_slippage),
                    gas_buffer=float(CONFIG["execution"]["gas_buffer"])
                )
                return await tx.wait()
            except Exception as e:
                if attempt == CONFIG["execution"]["max_retries"] - 1:
                    raise StrategyError.ExecutionFailed(f"Transaction failed: {e}")
                await asyncio.sleep(CONFIG["execution"]["retry_delay"])

            

    def check_health(self) -> HealthStatus:
        """Check strategy health status"""
        if self.status != StrategyStatus.ACTIVE:
            return HealthStatus.INACTIVE

        if not self.last_execution:
            return HealthStatus.PENDING

        now = datetime.now()
        time_since_last = (now - self.last_execution).total_seconds()
        expected_interval = self.config.interval.seconds

        # Calculate how overdue we are
        overdue_ratio = time_since_last / expected_interval

        if overdue_ratio >= CONFIG["health"]["critical_threshold"]:
            return HealthStatus.CRITICAL
        elif overdue_ratio >= CONFIG["health"]["warning_threshold"]:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY

    @classmethod
    def create_new(cls, **kwargs) -> 'Strategy':
        """Create new strategy with validation"""
        config = DCAConfig(**kwargs)
        config.validate()
        
        # Generate unique strategy ID
        strategy_id = f"dca_{kwargs['token_address']}_{int(datetime.now().timestamp())}"
        
        return cls(
            id=strategy_id,
            config=config,
            status=StrategyStatus.ACTIVE,
            start_time=datetime.now(),
            metadata={
                "creation_time": datetime.now().isoformat(),
                "status_history": []
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary"""
        return {
            "id": self.id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "current_period": self.current_period,
            "start_time": self.start_time.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "history": self.history,
            "metadata": self.metadata,
            "metrics": self.calculate_metrics().to_dict()
        }

class StrategyStore(Protocol):
    """Strategy persistence protocol"""
    @abstractmethod
    def save(self, strategy: Strategy) -> None: pass
    @abstractmethod
    def load(self, strategy_id: str) -> Optional[Strategy]: pass
    @abstractmethod
    def delete(self, strategy_id: str) -> None: pass
    @abstractmethod
    def list_all(self) -> List[Strategy]: pass

class JsonFileStrategyStore(StrategyStore):
    """JSON file-based strategy storage implementation"""
    def __init__(self, filepath: str = "dca_strategies.json"):
        self.filepath = Path(filepath)
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create storage file if it doesn't exist"""
        if not self.filepath.exists():
            self.filepath.write_text("{}")

    def _with_file_lock(self, operation: Callable[[], T]) -> T:
        """Execute operation with file lock"""
        with self._lock:
            return operation()

    def save(self, strategy: Strategy) -> None:
        """Save strategy with atomic file write"""
        def _save():
            strategies = self._load_file()
            strategies[strategy.id] = strategy.to_dict()
            self._save_file(strategies)
        self._with_file_lock(_save)

    def load(self, strategy_id: str) -> Optional[Strategy]:
        """Load strategy by ID"""
        strategies = self._with_file_lock(self._load_file)
        if strategy_data := strategies.get(strategy_id):
            return Strategy.from_dict(strategy_data)
        return None

    def delete(self, strategy_id: str) -> None:
        """Delete strategy by ID"""
        def _delete():
            strategies = self._load_file()
            if strategy_id in strategies:
                del strategies[strategy_id]
                self._save_file(strategies)
        self._with_file_lock(_delete)

    def list_all(self) -> List[Strategy]:
        """List all stored strategies"""
        return [
            Strategy.from_dict(data) 
            for data in self._with_file_lock(self._load_file).values()
        ]

    def _load_file(self) -> Dict[str, Any]:
        """Load JSON file contents"""
        try:
            return json.loads(self.filepath.read_text())
        except Exception as e:
            logger.error(f"Error loading strategies: {e}")
            raise StrategyError.ExecutionFailed(f"Failed to load strategies: {e}")

    def _save_file(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file"""
        self.filepath.write_text(json.dumps(data, indent=4))