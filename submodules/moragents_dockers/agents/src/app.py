import json
import os
import logging
from config import Config
from llama_cpp import Llama
from flask_cors import CORS
from flask import Flask, request, jsonify
from langchain_community.llms import Ollama
from delegator import Delegator
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
from langchain_community.embeddings import OllamaEmbeddings


def load_llm():
    llm = Llama(
        model_path=Config.MODEL_PATH,
        chat_format="functionary-v2",
        tokenizer=LlamaHFTokenizer.from_pretrained("meetkai/functionary-small-v2.4-GGUF"),
        n_gpu_layers=0,
        n_batch=4000,
        n_ctx=4000
    )
    return llm


llm = load_llm()

app = Flask(__name__)
CORS(app)

upload_state = False
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_LENGTH

llm_ollama = Ollama(model="llama3", base_url=Config.OLLAMA_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=Config.OLLAMA_URL)

logging.basicConfig(level=logging.DEBUG)

delegator = Delegator(Config.DELEGATOR_CONFIG, llm, llm_ollama, embeddings, app)
messages = [{'role': "assistant", "content": "This highly experimental chatbot is not intended for making important decisions, and its responses are generated based on incomplete data and algorithms that may evolve rapidly. By using this chatbot, you acknowledge that you use it at your own discretion and assume all risks associated with its limitations and potential errors."}]

next_turn_agent = None


@app.route('/', methods=['POST'])
def chat():
    global next_turn_agent, messages
    data = request.get_json()
    try:
        if 'prompt' in data:
            prompt = data['prompt']
            messages.append(prompt)
        if not next_turn_agent:
            result = delegator.get_delegator_response(prompt, upload_state)
            if "tool_calls" not in result:
                messages.append({"role": "assistant", "content": result["content"]})
                return jsonify({"role": "assistant", "content": result["content"]})
            else:
                if not result["tool_calls"]:
                    messages.append({"role": "assistant", "content": result["content"]})
                    return jsonify({"role": "assistant", "content": result["content"]})
                res = json.loads(result['tool_calls'][0]['function']['arguments'])
                response_swap = delegator.delegate_chat(res["next"], request)
                if "next_turn_agent" in response_swap.keys():
                    next_turn_agent = response_swap["next_turn_agent"]
                response = {"role": response_swap["role"], "content": response_swap["content"]}
        else:
            response_swap = delegator.delegate_chat(next_turn_agent, request)
            next_turn_agent = response_swap["next_turn_agent"]
            response = {"role": response_swap["role"], "content": response_swap["content"]}
        messages.append(response)
        return jsonify(response)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@app.route('/tx_status', methods=['POST'])
def swap_agent_tx_status():
    global messages
    response = delegator.delegate_route("crypto swap agent", request, "tx_status")
    messages.append(response)
    return jsonify(response)


@app.route('/messages', methods=['GET'])
def get_messages():
    global messages
    return jsonify({"messages": messages})


@app.route('/clear_messages', methods=['GET'])
def clear_messages():
    global messages
    messages = [{'role': "assistant", "content": "This highly experimental chatbot is not intended for making important decisions, and its responses are generated based on incomplete data and algorithms that may evolve rapidly. By using this chatbot, you acknowledge that you use it at your own discretion and assume all risks associated with its limitations and potential errors."}]
    return jsonify({"response": "successfully cleared message history"})


@app.route('/allowance', methods=['POST'])
def swap_agent_allowance():
    return delegator.delegate_route("crypto swap agent", request, "get_allowance")


@app.route('/approve', methods=['POST'])
def swap_agent_approve():
    return delegator.delegate_route("crypto swap agent", request, "approve")


@app.route('/swap', methods=['POST'])
def swap_agent_swap():
    return delegator.delegate_route("crypto swap agent", request, "swap")


@app.route('/upload', methods=['POST'])
def rag_agent_upload():
    global messages, upload_state
    response = delegator.delegate_route("rag agent", request, "upload_file")
    messages.append(response)
    upload_state = True
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
