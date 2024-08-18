from flask_cors import CORS
from flask import Flask, request, jsonify
from config import Config
from swap_agent.src import agent as swap_agent
from data_agent.src import agent as data_agent
from rag_agent.src import agent as rag_agent
from llama_cpp import Llama
from llama_cpp.llama_tokenizer import LlamaHFTokenizer
import os 
import logging
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from rag_agent.src.config import Config as ollama_config



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


llm=load_llm()

app = Flask(__name__)
CORS(app)

upload_state=False
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = ollama_config.MAX_LENGTH

llm_ollama = Ollama(model="llama3",base_url=ollama_config.URL) 
embeddings = OllamaEmbeddings(model="nomic-embed-text",base_url=ollama_config.URL)

logging.basicConfig(level=logging.DEBUG)


agent =  None
messages=[]
prompt = ChatPromptTemplate.from_template(
    """
            Answer the following question only based on the given context
                                                    
            <context>
            {context}
            </context>
                                                    
            Question: {input}
"""
)

@app.route('/swap_agent/', methods=['POST'])
def swap_agent_chat():
    global llm
    return swap_agent.chat(request, llm)

@app.route('/swap_agent/tx_status', methods=['POST'])
def swap_agent_tx_status():
    return swap_agent.tx_status(request)

@app.route('/swap_agent/messages', methods=['GET'])
def swap_agent_messages():
    return swap_agent.get_messages()
    
@app.route('/swap_agent/clear_messages', methods=['GET'])
def swap_agent_clear_messages():
    return swap_agent.clear_messages()
       
@app.route('/swap_agent/allowance', methods=['POST'])
def swap_agent_allowance():
    return swap_agent.get_allowance(request)
    
@app.route('/swap_agent/approve', methods=['POST'])
def swap_agent_approve():
    return swap_agent.approve(request)
    
@app.route('/swap_agent/swap', methods=['POST'])
def swap_agent_swap():   
    return swap_agent.swap(request)

@app.route('/data_agent/', methods=['POST'])
def data_agent_chat():
    global llm
    return data_agent.chat(request, llm)


@app.route('/data_agent/messages', methods=['GET'])
def data_agent_messages():
    return data_agent.get_messages()

@app.route('/data_agent/clear_messages', methods=['GET'])
def data_agent_clear_messages():
    return data_agent.clear_messages()

@app.route('/rag_agent/upload', methods=['POST'])
def rag_agent_upload():
    global llm_ollama,UPLOAD_FOLDER,embeddings
    return rag_agent.upload_file(request, UPLOAD_FOLDER, llm_ollama, embeddings,ollama_config.MAX_FILE_SIZE)

@app.route('/rag_agent/', methods=['POST'])
def rag_agent_chat():
    return rag_agent.chat(request)

@app.route('/rag_agent/messages', methods=['GET'])
def rag_agent_messages():
    return rag_agent.get_messages()

@app.route('/rag_agent/clear_messages', methods=['GET'])
def rag_agent_clear_messages():
    return rag_agent.clear_messages()

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)