import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.stores import chat_manager, agent_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claim", tags=["claim"])


@router.post("/claim")
async def claim(request: Request):
    """Process a claim request"""
    logger.info("Received claim request")
    try:
        claim_agent = agent_manager.get_agent("claim agent")
        if not claim_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Claim agent not found"},
            )

        response = await claim_agent.claim(request)
        chat_manager.add_message(response)
        return response
    except Exception as e:
        logger.error(f"Failed to process claim: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to process claim: {str(e)}"},
        )