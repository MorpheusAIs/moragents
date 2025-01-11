import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.stores import chat_manager_instance, agent_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/swap", tags=["swap"])


@router.post("/tx_status")
async def tx_status(request: Request):
    """Check transaction status"""
    logger.info("Received tx_status request")
    try:
        swap_agent = agent_manager_instance.get_agent("crypto swap")
        if not swap_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Crypto swap agent not found"},
            )

        response = await swap_agent.tx_status(request)
        chat_manager_instance.add_response(response.dict(), "swap")
        return response
    except Exception as e:
        logger.error(f"Failed to check tx status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to check tx status: {str(e)}"},
        )


@router.post("/allowance")
async def allowance(request: Request):
    """Get token allowance"""
    logger.info("Received allowance request")
    try:
        swap_agent = agent_manager_instance.get_agent("crypto swap")
        if not swap_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Crypto swap agent not found"},
            )

        response = await swap_agent.get_allowance(request)
        return response
    except Exception as e:
        logger.error(f"Failed to get allowance: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to get allowance: {str(e)}"},
        )


@router.post("/approve")
async def approve(request: Request):
    """Approve token spending"""
    logger.info("Received approve request")
    try:
        swap_agent = agent_manager_instance.get_agent("crypto swap")
        if not swap_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Crypto swap agent not found"},
            )

        response = await swap_agent.approve(request)
        return response
    except Exception as e:
        logger.error(f"Failed to approve: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to approve: {str(e)}"},
        )


@router.post("/swap")
async def swap(request: Request):
    """Execute token swap"""
    logger.info("Received swap request")
    try:
        swap_agent = agent_manager_instance.get_agent("crypto swap")
        if not swap_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Crypto swap agent not found"},
            )

        response = await swap_agent.swap(request)
        return response
    except Exception as e:
        logger.error(f"Failed to swap: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to swap: {str(e)}"},
        )
