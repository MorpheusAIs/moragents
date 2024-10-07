import os
import logging
import time

from flask_cors import CORS
from flask import Flask, request, jsonify

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from src.config import Config
from src.delegator import Delegator
from src.agent_manager import AgentManager
from src.models.messages import ChatRequest

# Constants
INITIAL_MESSAGE = {
    "role": "assistant",
    "content": "This highly experimental chatbot is not intended for making important decisions, and its responses are generated based on incomplete data and algorithms that may evolve rapidly. By using this chatbot, you acknowledge that you use it at your own discretion and assume all risks associated with its limitations and potential errors.",
}
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

upload_state = False
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_LENGTH

llm_ollama = Ollama(model="llama3.2", base_url=Config.OLLAMA_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=Config.OLLAMA_URL)

delegator = Delegator(Config.DELEGATOR_CONFIG, llm_ollama, llm_ollama, embeddings, app)
agent_manager = AgentManager()
messages = [INITIAL_MESSAGE]
next_turn_agent = None


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    user_id = chat_request.user_id
    prompt = chat_request.prompt.dict()

    logger.info(f"Received chat request for user {user_id}: {prompt}")

    try:
        active_agent = agent_manager.get_active_agent(user_id)

        if not active_agent:
            logger.info(
                f"No active agent for user {user_id}, getting delegator response"
            )

            start_time = time.time()
            result = delegator.get_delegator_response(
                prompt["content"], False
            )  # Assuming upload_state is False
            end_time = time.time()
            logger.info(f"Delegator response time: {end_time - start_time:.2f} seconds")
            logger.info(f"Delegator response: {result}")

            if "next" not in result:
                logger.error(f"Missing 'next' key in delegator response: {result}")
                raise ValueError("Invalid delegator response: missing 'next' key")

            active_agent = result["next"]
            agent_manager.set_active_agent(user_id, active_agent)

        logger.info(
            f"Delegating chat to active agent for user {user_id}: {active_agent}"
        )
        current_agent, response = delegator.delegate_chat(active_agent, chat_request)

        if isinstance(response, dict) and "role" in response and "content" in response:
            response_with_agent = response.copy()
            response_with_agent["agentName"] = current_agent or "Unknown"

            logger.info(f"Sending response for user {user_id}: {response_with_agent}")
            return response_with_agent
        else:
            logger.error(f"Invalid response format for user {user_id}: {response}")
            raise HTTPException(status_code=500, detail="Invalid response format")

    except TimeoutError:
        logger.error(f"Chat request timed out for user {user_id}")
        raise HTTPException(status_code=504, detail="Request timed out")
    except ValueError as ve:
        logger.error(f"Input formatting error for user {user_id}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat route for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Example curl command for the / endpoint


@app.route("/tx_status", methods=["POST"])
def swap_agent_tx_status():
    logger.info("Received tx_status request")
    response = delegator.delegate_route("crypto swap agent", request, "tx_status")
    messages.append(response)
    return jsonify(response)


@app.route("/messages", methods=["GET"])
def get_messages():
    logger.info("Received get_messages request")
    return jsonify({"messages": messages})


@app.route("/clear_messages", methods=["GET"])
def clear_messages():
    global messages
    logger.info("Clearing message history")
    messages = [INITIAL_MESSAGE]
    return jsonify({"response": "successfully cleared message history"})


@app.route("/allowance", methods=["POST"])
def swap_agent_allowance():
    logger.info("Received allowance request")
    return delegator.delegate_route("crypto swap agent", request, "get_allowance")


@app.route("/approve", methods=["POST"])
def swap_agent_approve():
    logger.info("Received approve request")
    return delegator.delegate_route("crypto swap agent", request, "approve")


@app.route("/swap", methods=["POST"])
def swap_agent_swap():
    logger.info("Received swap request")
    return delegator.delegate_route("crypto swap agent", request, "swap")


@app.route("/upload", methods=["POST"])
def rag_agent_upload():
    global messages, upload_state
    logger.info("Received upload request")
    response = delegator.delegate_route(
        "general purpose and context-based rag agent", request, "upload_file"
    )
    messages.append(response)
    upload_state = True
    return jsonify(response)


@app.route("/regenerate_tweet", methods=["POST"])
def regenerate_tweet():
    logger.info("Received generate tweet request")
    return delegator.delegate_route("tweet sizzler agent", None, "generate_tweet")


@app.route("/post_tweet", methods=["POST"])
def post_tweet():
    logger.info("Received x post request")
    return delegator.delegate_route("tweet sizzler agent", request, "post_tweet")


# TODO: Persist the X API key in the database (once we set this up)
@app.route("/set_x_api_key", methods=["POST"])
def set_x_api_key():
    logger.info("Received set X API key request")
    return delegator.delegate_route("tweet sizzler agent", request, "set_x_api_key")


@app.route("/claim", methods=["POST"])
def claim_agent_claim():
    logger.info("Received claim request")
    return delegator.delegate_route("claim agent", request, "claim")


# @app.route("/claim_status", methods=["POST"])
# def update_claim_status():
#     return claim_agent.claim_status(request)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
