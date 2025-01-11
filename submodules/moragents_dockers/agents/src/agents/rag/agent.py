import logging
import os

from fastapi import Request
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from werkzeug.utils import secure_filename

from src.agents.agent_core.agent import AgentCore
from src.models.core import ChatRequest, AgentResponse
from src.stores import chat_manager_instance

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")


class RagAgent(AgentCore):
    """Agent for handling document Q&A using RAG."""

    def __init__(self, config, llm, embeddings):
        super().__init__(config, llm, embeddings)
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
        vector_store = FAISS.from_documents(split_documents, self.embeddings)
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 7})

    async def upload_file(self, request: Request):
        self.logger.info(f"Received upload request: {request}")
        file = request["file"]
        if file.filename == "":
            return AgentResponse.needs_info(content="Please select a file to upload")

        # Check file size to ensure it's less than 5 MB
        content = await file.read()
        await file.seek(0)
        if len(content) > self.max_size:
            return AgentResponse.needs_info(content="The file is too large. Please upload a file less than 5 MB")

        try:
            await self.handle_file_upload(file)
            chat_manager_instance.set_uploaded_file(True)
            return AgentResponse.success(content="You have successfully uploaded the text")
        except Exception as e:
            self.logger.error(f"Error during file upload: {str(e)}")
            return AgentResponse.error(
                error_message=f"There was an issue uploading your file: {str(e)}. Please try again with a different file."
            )

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for RAG."""
        try:
            if not chat_manager_instance.get_uploaded_file_status():
                return AgentResponse.needs_info(content="Please upload a file first")

            prompt = request.prompt.content
            response = await self._get_rag_response(prompt)
            return AgentResponse.success(content=response)

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(
                error_message=f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question."
            )

    async def _get_rag_response(self, prompt: str) -> str:
        retrieved_docs = self.retriever.invoke(prompt)
        formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        formatted_prompt = f"Question: {prompt}\n\nContext: {formatted_context}"
        system_prompt = "You are a helpful assistant. Use the provided context to respond to the following question."

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": formatted_prompt},
        ]
        result = self.llm.invoke(messages)
        return result.content.strip()

    async def _execute_tool(self, func_name: str, args: dict) -> AgentResponse:
        """Not used in RAG agent but required by AgentCore."""
        return AgentResponse.needs_info(
            content="This operation is not supported. Please try asking a question about the uploaded document instead."
        )
