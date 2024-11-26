import logging
from fastapi import APIRouter
from src.stores import chat_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages")
async def get_messages():
    """Get all chat messages"""
    logger.info("Received get_messages request")
    return {"messages": chat_manager.get_messages()}


@router.get("/clear")
async def clear_messages():
    """Clear chat message history"""
    logger.info("Clearing message history")
    chat_manager.clear_messages()
    return {"response": "successfully cleared message history"}
