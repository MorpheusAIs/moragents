import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.stores import chat_manager_instance, agent_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crypto_data", tags=["crypto_data"])


@router.post("/process_data")
async def process_data(data: dict):
    """Process crypto data"""
    logger.info("Data Agent: Received process_data request")
    try:
        crypto_agent = agent_manager_instance.get_agent("crypto data")
        if not crypto_agent:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Crypto data agent not found"},
            )

        response = await crypto_agent.process_data(data)
        chat_manager_instance.add_message(response)
        return response
    except Exception as e:
        logger.error(f"Failed to process data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to process data: {str(e)}"},
        )
