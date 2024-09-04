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



class RagAgent:
    def __init__(self, config, llm, llm_ollama, embeddings,flask_app):
        self.llm = llm_ollama
        self.flask_app = flask_app
        self.embedding=embeddings
        self.config = config
        self.agent = None
        self.messages = [{'role': "assistant", "content": "Please upload a file to begin"}]
        self.upload_state = False
        self.prompt = ChatPromptTemplate.from_template(
            """
                Answer the following question only based on the given context
                                                        
                <context>
                {context}
                </context>
                                                        
                Question: {input}
            """
        )
        self.UPLOAD_FOLDER = flask_app.config['UPLOAD_FOLDER']
        self.max_size = 5 * 1024 * 1024
        self.retriever = None
    

    def handle_file_upload(self,file):
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        file.save(os.path.join(self.UPLOAD_FOLDER, filename))
        # DocumentToolsGenerator class instantiation 
        loader = PyMuPDFLoader(os.path.join(self.UPLOAD_FOLDER,filename))
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024,chunk_overlap=20,length_function=len,is_separator_regex=False)
        split_documents = text_splitter.split_documents(docs)
        vector_store = FAISS.from_documents(split_documents, self.embedding)
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 7})


    def upload_file(self,request):
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0, 0)  # Reset the file pointer to the beginning
        if file_length > self.max_size:
            return {"role": "assistant", "content": 'please use a file less than 5 MB'}
        try:
            self.handle_file_upload(file)
            self.upload_state = True
            return {"role": "assistant", "content": 'You have successfully uploaded the text'}
        except Exception as e:
            logging.error(f'Error during file upload: {str(e)}')
            return {'error': str(e)}, 500

    def chat(self,request):
        try:
            data = request.get_json()
            if 'prompt' in data:
                prompt = data['prompt']['content']
                role = "assistant"
                retrieved_docs = self.retriever.invoke(prompt)
                formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
                formatted_prompt = f"Question: {prompt}\n\nContext: {formatted_context}"
                answer=self.llm(formatted_prompt)
                response = answer  if self.upload_state else "please upload a file first"
                return {"role": role, "content": response}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logging.error(f'Error in chat endpoint: {str(e)}')
            return {"Error": str(e)}, 500