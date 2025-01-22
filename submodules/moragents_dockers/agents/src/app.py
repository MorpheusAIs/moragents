import logging
import os
import time
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama

from src.config import Config, load_agent_routes
from src.delegator import Delegator
from src.models.service.chat_models import AgentResponse, ChatRequest
from src.stores import (
    agent_manager_instance,
    chat_manager_instance,
    workflow_manager_instance,
)

# Configure routes
from src.routes import (
    agent_manager_routes,
    chat_manager_routes,
    key_manager_routes,
    wallet_manager_routes,
    workflow_manager_routes,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup constants and directories
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize LLM and embeddings
llm = ChatOllama(
    model=Config.OLLAMA_MODEL,
    base_url=Config.OLLAMA_URL,
)
embeddings = OllamaEmbeddings(model=Config.OLLAMA_EMBEDDING_MODEL, base_url=Config.OLLAMA_URL)

# Initialize delegator
delegator = Delegator(llm, embeddings)

# Include core routers
ROUTERS = [
    agent_manager_routes.router,
    key_manager_routes.router,
    chat_manager_routes.router,
    wallet_manager_routes.router,
    workflow_manager_routes.router,
]

# Dynamically load and add agent routers
agent_routers = load_agent_routes()
for router in agent_routers:
    app.include_router(router)


for router in ROUTERS:
    app.include_router(router)


async def get_active_agent_for_chat(prompt: Dict[str, Any]) -> str:
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


@app.on_event("startup")
async def startup_event():
    """Initialize workflow manager on startup"""
    await workflow_manager_instance.initialize()


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """Handle chat requests and delegate to appropriate agent"""
    logger.info(f"Received chat request for conversation {chat_request.conversation_id}")

    try:
        # Parse command if present
        agent_name, message = agent_manager_instance.parse_command(chat_request.prompt.content)

        if agent_name:
            agent_manager_instance.set_active_agent(agent_name)
            chat_request.prompt.content = message
        else:
            agent_manager_instance.clear_active_agent()

        # Add user message to chat history
        chat_manager_instance.add_message(chat_request.prompt.dict(), chat_request.conversation_id)

        # If command was parsed, use that agent directly
        if agent_name:
            logger.info(f"Using command agent flow: {agent_name}")
            agent = agent_manager_instance.get_agent(agent_name)
            if not agent:
                logger.error(f"Agent {agent_name} not found")
                raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

            agent_response = await agent.chat(chat_request)
            current_agent = agent_name

        # Otherwise use delegator to find appropriate agent
        else:
            logger.info("Using delegator flow")
            delegator.reset_attempted_agents()
            active_agent = await get_active_agent_for_chat(chat_request.prompt.dict())
            current_agent, agent_response = await delegator.delegate_chat(active_agent, chat_request)

        # We only critically fail if we don't get an AgentResponse
        if not isinstance(agent_response, AgentResponse):
            logger.error(f"Agent {current_agent} returned invalid response type {type(agent_response)}")
            raise HTTPException(status_code=500, detail="Agent returned invalid response type")

        # Convert to API response and add to chat history
        chat_manager_instance.add_response(agent_response.dict(), current_agent, chat_request.conversation_id)

        logger.info(f"Sending response: {agent_response.dict()}")
        return agent_response.dict()

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
