import logging
from fastapi import APIRouter, Query
from src.stores import chat_manager_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages")
async def get_messages(conversation_id: str = Query(default="default")):
    """Get all chat messages for a conversation"""
    logger.info(f"Received get_messages request for conversation {conversation_id}")
    return {"messages": chat_manager_instance.get_messages(conversation_id)}


@router.get("/clear")
async def clear_messages(conversation_id: str = Query(default="default")):
    """Clear chat message history for a conversation"""
    logger.info(f"Clearing message history for conversation {conversation_id}")
    chat_manager_instance.clear_messages(conversation_id)
    return {"response": "successfully cleared message history"}


@router.get("/conversations")
async def get_conversations():
    """Get all conversation IDs"""
    logger.info("Getting all conversation IDs")
    return {"conversation_ids": chat_manager_instance.get_all_conversation_ids()}


@router.post("/conversations")
async def create_conversation():
    """Create a new conversation"""
    new_id = f"conversation_{len(chat_manager_instance.get_all_conversation_ids())}"
    conversation = chat_manager_instance.create_conversation(new_id)
    logger.info(f"Created new conversation with ID: {new_id}")
    return {"conversation_id": new_id, "conversation": conversation}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    logger.info(f"Deleting conversation {conversation_id}")
    chat_manager_instance.delete_conversation(conversation_id)
    return {"response": f"successfully deleted conversation {conversation_id}"}
