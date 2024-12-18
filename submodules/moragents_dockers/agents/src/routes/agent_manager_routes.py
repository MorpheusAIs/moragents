import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import agent_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/available")
async def get_available_agents() -> JSONResponse:
    """Get the list of currently available agents"""
    return JSONResponse(
        content={
            "selected_agents": agent_manager_instance.get_selected_agents(),
            "available_agents": agent_manager_instance.get_available_agents(),
        }
    )


@router.post("/selected")
async def set_selected_agents(request: Request) -> JSONResponse:
    """Set which agents should be selected"""
    data = await request.json()
    agent_names = data.get("agents", [])

    agent_manager_instance.set_selected_agents(agent_names)
    logger.info(f"Newly selected agents: {agent_manager_instance.get_selected_agents()}")

    return JSONResponse(content={"status": "success", "agents": agent_names})


@router.get("/commands")
async def get_agent_commands() -> JSONResponse:
    """Get the list of available agent commands"""
    available_agents = agent_manager_instance.get_available_agents()
    commands = [
        {
            "command": agent["command"],
            "description": agent["description"],
            "name": agent["human_readable_name"],
        }
        for agent in available_agents
    ]
    return JSONResponse(content={"commands": commands})
