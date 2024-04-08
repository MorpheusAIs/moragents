import tools
from flask import Flask, request, jsonify
from huggingface_hub import hf_hub_download
from langchain_community.llms import LlamaCpp
from langchain.agents import initialize_agent
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from config import Config


def download_model(model_name, revision):
    model_directory = hf_hub_download(repo_id=model_name, filename=revision)
    return model_directory


def load_llm():
    model_path = Config.MODEL_PATH
    n_gpu_layers = 0
    n_batch = 1024
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx=1024,
        f16_kv=True,
        use_mlock=True,
        use_mmap=True,
        callback_manager=callback_manager,
        temperature=0.1,
        streaming=False
    )

    return llm


def load_agent(tools):
    PREFIX = "<<SYS>> You are smart agent that selects a function from list of functions based on user queries.\\ When the function throws Error Tell the user why u stopped and about the error from the description\\ Run only one function tool at a time in one query.<</SYS>>\\n"
    llm = load_llm()
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True,
        max_iterations=1,
        early_stopping_method="generate",
        agent_kwargs={
            'prefix': PREFIX
        }
    )
    return agent


tools_provided = tools.get_tools()
agent = load_agent(tools_provided)
app = Flask(__name__)


@app.route('/', methods=['POST'])
def generate_response():
    global agent
    try:
        data = request.get_json()

        if agent is None:
            agent = load_agent(tools)

        if 'prompt' in data:
            prompt = data['prompt']
            response = agent.run(prompt)
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
