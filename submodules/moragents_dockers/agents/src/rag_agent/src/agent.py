from flask import jsonify
import os 
import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from werkzeug.utils import secure_filename


logging.basicConfig(level=logging.DEBUG)


agent =  None
messages=[{'role':"assistant","content":"Please upload a file to begin"}]
upload_state = False
prompt = ChatPromptTemplate.from_template(
    """
            Answer the following question only based on the given context
                                                    
            <context>
            {context}
            </context>
                                                    
            Question: {input}
"""
)

def handle_file_upload(file,UPLOAD_FOLDER,llm,embeddings):
    global agent,prompt
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    # DocumentToolsGenerator class instantiation 
    loader = PyMuPDFLoader(os.path.join(UPLOAD_FOLDER,filename))
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    split_documents = text_splitter.split_documents(docs)
    vector_store = FAISS.from_documents(split_documents, embeddings)
    docs_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_store.as_retriever()
    agent = create_retrieval_chain(retriever, docs_chain)


def upload_file(request,UPLOAD_FOLDER,llm,embeddings,MAX_SIZE):
    global upload_state
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # Check file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)  # Reset the file pointer to the beginning
    if file_length > MAX_SIZE:
        messages.append({"role": "assistant", "content": 'please use a file less than 5 MB'})
        return jsonify({"role": "assistant", "content": 'please use a file less than 5 MB'})
    try:
        handle_file_upload(file,UPLOAD_FOLDER,llm,embeddings)
        upload_state = True
        messages.append({"role": "assistant", "content": 'You have successfully uploaded the text'})
        return jsonify({"role": "assistant", "content": 'You have successfully uploaded the text'})
    except Exception as e:
        logging.error(f'Error during file upload: {str(e)}')
        return jsonify({'error': str(e)}), 500

def chat(request):
    global messages,upload_state,agent
    try:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']['content']
            messages.append(data['prompt'])
            role = "assistant"
            response = agent.invoke({"input": prompt})  if upload_state else {"answer":"please upload a file first"}
        
            messages.append({"role": role, "content": response["answer"]})
            return jsonify({"role": role, "content": response["answer"]})
        else:
            return jsonify({"error": "Missing required parameters"}), 400
    except Exception as e:
        logging.error(f'Error in chat endpoint: {str(e)}')
        return jsonify({"Error": str(e)}), 500

def get_messages():
    global messages
    return jsonify({"messages": messages})

def clear_messages():
    global messages
    messages = [{'role':"assistant","content":"Please upload a file to begin"}]
    return jsonify({"response": "successfully cleared message history"})

