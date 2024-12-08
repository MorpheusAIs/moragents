import logging
import os

from fastapi import Request
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from werkzeug.utils import secure_filename

from src.models.messages import ChatRequest
from src.stores import agent_manager_instance, chat_manager_instance

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")


class RagAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm
        self.embedding = embeddings
        self.messages = [{"role": "assistant", "content": "Please upload a file to begin"}]

        self.prompt = ChatPromptTemplate.from_template(
            """
                Answer the following question only based on the given context

                <context>
                {context}
                </context>

                Question: {input}
            """
        )
        self.max_size = 5 * 1024 * 1024
        self.retriever = None

    async def handle_file_upload(self, file):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # DocumentToolsGenerator class instantiation
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        split_documents = text_splitter.split_documents(docs)
        vector_store = FAISS.from_documents(split_documents, self.embedding)
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 7})

    async def upload_file(self, request: Request):
        logger.info(f"Received upload request: {request}")
        file = request["file"]
        if file.filename == "":
            return {"error": "No selected file"}, 400

        # Check file size to ensure it's less than 5 MB
        content = await file.read()
        await file.seek(0)
        if len(content) > self.max_size:
            return {"role": "assistant", "content": "Please use a file less than 5 MB"}

        try:
            await self.handle_file_upload(file)
            chat_manager_instance.set_uploaded_file(True)
            return {
                "role": "assistant",
                "content": "You have successfully uploaded the text",
            }
        except Exception as e:
            logging.error(f"Error during file upload: {str(e)}")
            return {"error": str(e)}, 500

    def _get_rag_response(self, prompt):
        retrieved_docs = self.retriever.invoke(prompt)
        formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        formatted_prompt = f"Question: {prompt}\n\nContext: {formatted_context}"
        selected_agents = agent_manager_instance.get_selected_agents()
        agent_descriptions = "\n".join([f"- {agent['description']}" for agent in selected_agents])
        system_prompt = f"""
        You are a helpful assistant. Use the provided context to respond to the following question.
        The following agents are currently available:
        {agent_descriptions}"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": formatted_prompt},
        ]
        result = self.llm.invoke(messages)
        return result.content.strip()

    def chat(self, request: ChatRequest):
        try:
            data = request.dict()
            if "prompt" in data:
                prompt = data["prompt"]["content"]
                if chat_manager_instance.get_uploaded_file_status():
                    response = self._get_rag_response(prompt)
                else:
                    response = "Please upload a file first"
                return {"role": "assistant", "content": response}

            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logging.error(f"Error in chat endpoint: {str(e)}")
            raise e
