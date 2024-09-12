import os
import logging
import time
from functools import wraps
from config import Config
from llama_cpp import Llama, LLAMA_FTYPE_MOSTLY_Q4_0
from flask_cors import CORS
from flask import Flask, request, jsonify
from langchain_community.llms import Ollama
from delegator import Delegator
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
from langchain_community.embeddings import OllamaEmbeddings

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

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message="Function call timed out"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function call failed: {str(e)}")
                raise TimeoutError(error_message)

        return wrapper

    return decorator


@timeout(30)
def load_llm():
    logger.info("Loading LLM model")
    try:
        llm = Llama(
            model_path=Config.MODEL_PATH,
            chat_format="functionary-v2",
            tokenizer=LlamaHFTokenizer.from_pretrained(
                "meetkai/functionary-small-v2.4-GGUF"
            ),
            n_gpu_layers=-1,  # Use all available GPU layers
            n_batch=1024,  # Increase batch size for faster processing
            n_ctx=1024,  # Increase context size for better performance
            verbose=False,  # Disable verbose output for speed
            use_mlock=True,  # Lock memory to prevent swapping
            use_mmap=True,  # Use memory mapping for faster loading
            n_threads=16,  # Increase number of threads for more parallel processing
        )
        logger.info("LLM model loaded successfully")
        return llm
    except Exception as e:
        logger.error(f"Error loading LLM model: {str(e)}")
        raise


app = Flask(__name__)
CORS(app)

upload_state = False
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_LENGTH

try:
    llm = load_llm()
except TimeoutError:
    logger.error("LLM loading timed out")
    llm = None
except Exception as e:
    logger.error(f"Failed to load LLM: {str(e)}")
    llm = None

llm_ollama = Ollama(model="llama3", base_url=Config.OLLAMA_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=Config.OLLAMA_URL)

delegator = Delegator(Config.DELEGATOR_CONFIG, llm, llm_ollama, embeddings, app)
messages = [INITIAL_MESSAGE]
next_turn_agent = None


@app.route("/", methods=["POST"])
@timeout(60, "Chat request timed out")
def chat():
    global next_turn_agent, messages
    data = request.get_json()
    logger.info(f"Received chat request: {data}")
    print("data", data)
    try:
        current_agent = None
        if "prompt" in data:
            prompt = data["prompt"]
            messages.append(prompt)

        if not next_turn_agent:
            logger.info("No next turn agent, getting delegator response")
            start_time = time.time()
            result = delegator.get_delegator_response(prompt, upload_state)
            end_time = time.time()
            logger.info(f"Delegator response time: {end_time - start_time:.2f} seconds")
            logger.info(f"Delegator response: {result}")

            if "next" not in result:
                logger.error(f"Missing 'next' key in delegator response: {result}")
                raise ValueError("Invalid delegator response: missing 'next' key")

            next_agent = result["next"]
            current_agent, response_swap = delegator.delegate_chat(next_agent, request)
        else:
            logger.info(f"Delegating chat to next turn agent: {next_turn_agent}")
            current_agent, response_swap = delegator.delegate_chat(
                next_turn_agent, request
            )

        # Handle both dictionary and tuple returns from delegate_chat
        if isinstance(response_swap, tuple):
            response, status_code = response_swap
            next_turn_agent = None  # Reset next_turn_agent if we got an error response
        else:
            response = response_swap
            next_turn_agent = response_swap.get("next_turn_agent")
            status_code = 200

        if isinstance(response, dict) and "role" in response and "content" in response:
            # Add agentName to the response if available
            response_with_agent = response.copy()
            if current_agent:
                response_with_agent["agentName"] = current_agent

            messages.append(response_with_agent)

            logger.info(f"Sending response: {response_with_agent}")
            return jsonify(response_with_agent), status_code
        else:
            logger.error(f"Invalid response format: {response}")
            return jsonify({"error": "Invalid response format"}), 500

    except TimeoutError:
        logger.error("Chat request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except ValueError as ve:
        logger.error(f"Input formatting error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


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


@app.route("/post_tweet", methods=["POST"])
def post_tweet():
    logger.info("Received x post request")
    return delegator.delegate_route("tweet sizzler agent", request, "post_tweet")


# TODO: Persist the X API key in the database (once we set this up)
@app.route("/set_x_api_key", methods=["POST"])
def set_x_api_key():
    logger.info("Received set X API key request")
    return delegator.delegate_route("tweet sizzler agent", request, "set_x_api_key")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
