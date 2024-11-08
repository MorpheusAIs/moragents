import logging
import os
import time

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from src.config import Config
from src.delegator import Delegator
from src.models.messages import ChatRequest
from src.stores import agent_manager, chat_manager

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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

llm = ChatOllama(
    model=Config.OLLAMA_MODEL,
    base_url=Config.OLLAMA_URL,
)
embeddings = OllamaEmbeddings(model=Config.OLLAMA_EMBEDDING_MODEL, base_url=Config.OLLAMA_URL)

delegator = Delegator(agent_manager, llm, embeddings)


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    prompt = chat_request.prompt.dict()
    chat_manager.add_message(prompt)

    try:
        # Reset attempted agents at the start of each new chat request, for agent cascading
        delegator.reset_attempted_agents()

        active_agent = agent_manager.get_active_agent()

        if not active_agent:
            logger.info("No active agent, getting delegator response")

            start_time = time.time()
            result = delegator.get_delegator_response(prompt)

            end_time = time.time()

            logger.info(f"Delegator response time: {end_time - start_time:.2f} seconds")
            logger.info(f"Delegator response: {result}")

            if "agent" not in result:
                logger.error(f"Missing 'agent' key in delegator response: {result}")
                raise ValueError("Invalid delegator response: missing 'agent' key")

            active_agent = result["agent"]

        logger.info(f"Delegating chat to active agent: {active_agent}")
        current_agent, response = delegator.delegate_chat(active_agent, chat_request)

        if not current_agent:
            logger.error("All agents failed to provide a valid response")
            raise HTTPException(
                status_code=500,
                detail="All available agents failed to process the request",
            )

        if isinstance(response, tuple) and len(response) == 2:
            error_message, status_code = response
            logger.error(f"Error from agent: {error_message}")
            raise HTTPException(status_code=status_code, detail=error_message)

        if isinstance(response, dict) and "role" in response and "content" in response:
            chat_manager.add_response(response, current_agent)

            logger.info(f"Sending response: {response}")
            return response
        else:
            logger.error(f"Invalid response format: {response}")
            raise HTTPException(status_code=500, detail="Invalid response format")

    except TimeoutError:
        logger.error("Chat request timed out")
        raise HTTPException(status_code=504, detail="Request timed out")
    except ValueError as ve:
        logger.error(f"Input formatting error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tx_status")
async def swap_agent_tx_status(request: Request):
    logger.info("Received tx_status request")
    response = await delegator.delegate_route("crypto swap agent", request, "tx_status")
    chat_manager.add_message(response)
    return response


@app.get("/messages")
async def get_messages():
    logger.info("Received get_messages request")
    return {"messages": chat_manager.get_messages()}


@app.get("/clear_messages")
async def clear_messages():
    logger.info("Clearing message history")
    chat_manager.clear_messages()
    return {"response": "successfully cleared message history"}


@app.post("/allowance")
async def swap_agent_allowance(request: Request):
    logger.info("Received allowance request")
    return delegator.delegate_route("crypto swap agent", request, "get_allowance")


@app.post("/approve")
async def swap_agent_approve(request: Request):
    logger.info("Received approve request")
    return delegator.delegate_route("crypto swap agent", request, "approve")


@app.post("/swap")
async def swap_agent_swap(request: Request):
    logger.info("Received swap request")
    return delegator.delegate_route("crypto swap agent", request, "swap")


@app.post("/upload")
async def rag_agent_upload(file: UploadFile = File(...)):
    logger.info("Received upload request")
    response = await delegator.delegate_route("rag agent", {"file": file}, "upload_file")
    chat_manager.add_message(response)
    return response


@app.post("/regenerate_tweet")
async def regenerate_tweet():
    logger.info("Received generate tweet request")
    return delegator.delegate_route("tweet sizzler agent", None, "generate_tweet")


@app.post("/post_tweet")
async def post_tweet(request: Request):
    logger.info("Received x post request")
    return await delegator.delegate_route("tweet sizzler agent", request, "post_tweet")


@app.post("/set_x_api_key")
async def set_x_api_key(request: Request):
    logger.info("Received set X API key request")
    return await delegator.delegate_route("tweet sizzler agent", request, "set_x_api_key")


@app.post("/claim")
async def claim_agent_claim(request: Request):
    logger.info("Received claim request")
    return delegator.delegate_route("claim agent", request, "claim")


@app.get("/available-agents")
async def get_available_agents():
    """Get the list of currently available agents"""
    return {
        "selected_agents": agent_manager.get_selected_agents(),
        "available_agents": agent_manager.get_available_agents(),
    }


@app.post("/selected-agents")
async def set_selected_agents(request: Request):
    """Set which agents should be selected"""
    data = await request.json()
    agent_names = data.get("agents", [])

    agent_manager.set_selected_agents(agent_names)
    logger.info(f"Newly selected agents: {agent_manager.get_selected_agents()}")

    return {"status": "success", "agents": agent_names}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
