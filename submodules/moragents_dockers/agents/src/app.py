import logging
import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama

from src.config import Config
from src.delegator import Delegator
from src.models.messages import ChatRequest
from src.stores import agent_manager_instance, chat_manager_instance, workflow_manager_instance
from src.routes import (
    agent_manager_routes,
    chat_manager_routes,
    key_manager_routes,
    wallet_manager_routes,
    workflow_manager_routes,
)

# Constants
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await workflow_manager_instance.initialize()


@app.on_event("startup")
async def startup_event():
    await workflow_manager_instance.initialize()


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

llm = ChatOllama(
    model=Config.OLLAMA_MODEL,
    base_url=Config.OLLAMA_URL,
)
embeddings = OllamaEmbeddings(model=Config.OLLAMA_EMBEDDING_MODEL, base_url=Config.OLLAMA_URL)

delegator = Delegator(llm, embeddings)

# Include base store routes
app.include_router(agent_manager_routes.router)
app.include_router(key_manager_routes.router)
app.include_router(chat_manager_routes.router)
app.include_router(wallet_manager_routes.router)
app.include_router(workflow_manager_routes.router)

# Agent route imports
from src.agents.crypto_data.routes import router as crypto_router
from src.agents.rag.routes import router as rag_router
from src.agents.mor_claims.routes import router as claim_router
from src.agents.tweet_sizzler.routes import router as tweet_router
from src.agents.token_swap.routes import router as swap_router
from src.agents.dca_agent.routes import router as dca_router
from src.agents.base_agent.routes import router as base_router

# Include agent routes
app.include_router(crypto_router)
app.include_router(rag_router)
app.include_router(claim_router)
app.include_router(tweet_router)
app.include_router(swap_router)
app.include_router(dca_router)
app.include_router(base_router)


async def get_active_agent_for_chat(prompt: dict) -> str:
    """Get the active agent for handling the chat request."""
    active_agent = agent_manager_instance.get_active_agent()
    if active_agent:
        return active_agent

    logger.info("No active agent, getting delegator response")
    start_time = time.time()
    result = delegator.get_delegator_response(prompt)
    logger.info(f"Delegator response time: {time.time() - start_time:.2f} seconds")
    logger.info(f"Delegator response: {result}")

    if "agent" not in result:
        logger.error(f"Missing 'agent' key in delegator response: {result}")
        raise ValueError("Invalid delegator response: missing 'agent' key")

    return result["agent"]


def validate_agent_response(response: dict, current_agent: str) -> dict:
    """Validate and process the agent's response."""
    if not current_agent:
        logger.error("All agents failed to provide a valid response")
        raise HTTPException(
            status_code=500,
            detail="All available agents failed to process the request",
        )

    return response


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """Send a chat message and get a response"""
    logger.info(f"Received chat request for conversation {chat_request.conversation_id}")

    # Parse command if present
    agent_name, message = agent_manager_instance.parse_command(
        chat_request.prompt.dict()["content"]
    )

    if agent_name:
        # If command was used, set that agent as active
        agent_manager_instance.set_active_agent(agent_name)
        # Update message content without command
        chat_request.prompt.dict()["content"] = message

    chat_manager_instance.add_message(chat_request.prompt.dict(), chat_request.conversation_id)

    try:
        if not agent_name:
            delegator.reset_attempted_agents()
            active_agent = await get_active_agent_for_chat(chat_request.prompt.dict())
        else:
            active_agent = agent_name

        logger.info(f"Delegating chat to active agent: {active_agent}")
        current_agent, response = delegator.delegate_chat(active_agent, chat_request)

        validated_response = validate_agent_response(response, current_agent)
        chat_manager_instance.add_response(
            validated_response, current_agent, chat_request.conversation_id
        )

        logger.info(f"Sending response: {validated_response}")
        return validated_response

    except TimeoutError:
        logger.error("Chat request timed out")
        raise HTTPException(status_code=504, detail="Request timed out")
    except ValueError as ve:
        logger.error(f"Input formatting error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
