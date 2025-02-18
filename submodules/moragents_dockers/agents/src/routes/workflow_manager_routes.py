import logging
from datetime import timedelta
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import workflow_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/create")
async def create_workflow(request: Request) -> JSONResponse:
    """Create a new workflow"""
    try:
        data = await request.json()
        workflow = await workflow_manager_instance.create_workflow(
            name=data["name"],
            description=data["description"],
            action=data["action"],
            params=data["params"],
            interval=timedelta(seconds=data["interval"]),
            metadata=data.get("metadata"),
        )
        return JSONResponse(content={"status": "success", "workflow": workflow.to_dict()})
    except Exception as e:
        logger.error(f"Failed to create workflow: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.get("/list")
async def list_workflows() -> JSONResponse:
    """Get list of all workflows"""
    try:
        workflows = await workflow_manager_instance.list_workflows()
        return JSONResponse(content={"workflows": [w.to_dict() for w in workflows]})
    except Exception as e:
        logger.error(f"Failed to list workflows: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> JSONResponse:
    """Get workflow by ID"""
    try:
        workflow = await workflow_manager_instance.get_workflow(workflow_id)
        if workflow:
            return JSONResponse(content={"workflow": workflow.to_dict()})
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Workflow {workflow_id} not found"},
        )
    except Exception as e:
        logger.error(f"Failed to get workflow: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, request: Request) -> JSONResponse:
    """Update workflow properties"""
    try:
        updates = await request.json()
        workflow = await workflow_manager_instance.update_workflow(workflow_id, **updates)
        if workflow:
            return JSONResponse(content={"status": "success", "workflow": workflow.to_dict()})
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Workflow {workflow_id} not found"},
        )
    except Exception as e:
        logger.error(f"Failed to update workflow: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str) -> JSONResponse:
    """Delete a workflow"""
    try:
        success = await workflow_manager_instance.delete_workflow(workflow_id)
        if success:
            return JSONResponse(content={"status": "success"})
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Workflow {workflow_id} not found"},
        )
    except Exception as e:
        logger.error(f"Failed to delete workflow: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
