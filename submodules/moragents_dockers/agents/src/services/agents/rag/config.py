from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for RAG Agent."""

    # *************
    # AGENT CONFIG
    # ------------
    # This must be defined in every agent config file
    # It is required to load the agent
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.rag.agent",
        class_name="RAGAgent",
        description="Processes and analyzes uploaded documents to answer questions about their contents",
        human_readable_name="Document Q&A",
        command="rag",
        upload_required=True,
    )

    # *************
    # RAG CONFIG
    # *************

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    MAX_LENGTH = 16 * 1024 * 1024
