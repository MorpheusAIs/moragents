import logging
from fastapi import APIRouter, HTTPException
from src.models.service.chat_models import ChatRequest, AgentResponse
from src.stores import agent_manager_instance, chat_manager_instance
from src.delegator import Delegator
from src.controllers.chat_controller import ChatController
from src.config import llm, embeddings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat")
async def chat(chat_request: ChatRequest):
    """Handle chat requests and delegate to appropriate agent"""
    logger.info(f"Received chat request for conversation {chat_request.conversation_id}")

    # Initialize new delegator and controller for each request
    delegator = Delegator(llm, embeddings)
    controller = ChatController(delegator)

    try:
        response = await controller.handle_chat(chat_request)
        return response

    except HTTPException:
        raise
    except TimeoutError:
        logger.error("Chat request timed out")
        raise HTTPException(status_code=504, detail="Request timed out")
    except ValueError as ve:
        logger.error(f"Input formatting error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
