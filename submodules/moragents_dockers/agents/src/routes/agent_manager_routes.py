import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/available")
async def get_available_agents() -> JSONResponse:
    """Get the list of currently available agents"""
    return JSONResponse(
        content={
            "selected_agents": agent_manager.get_selected_agents(),
            "available_agents": agent_manager.get_available_agents(),
        }
    )


@router.post("/selected")
async def set_selected_agents(request: Request) -> JSONResponse:
    """Set which agents should be selected"""
    data = await request.json()
    agent_names = data.get("agents", [])

    agent_manager.set_selected_agents(agent_names)
    logger.info(f"Newly selected agents: {agent_manager.get_selected_agents()}")

    return JSONResponse(content={"status": "success", "agents": agent_names})
