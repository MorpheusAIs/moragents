import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from src.models.session import DBSessionFactory
from src.models.daos.conversation_dao import ConversationDAO
from src.models.service.service_models import ConversationModel

logger = logging.getLogger(__name__)


class ConversationController:
    """Controller for managing conversations."""

    def __init__(self, session: Optional[Session] = None, auto_close_session: Optional[bool] = None):
        self._auto_close_session = (session is None) if (auto_close_session is None) else auto_close_session
        self._session = session

    def __enter__(self):
        """Context manager entry point."""
        if self._session is None:
            self._session = DBSessionFactory.get_instance().new_session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit point."""
        if self._auto_close_session and self._session:
            self._session.close()

    def get_conversation(self, conversation_id: int) -> Optional[ConversationModel]:
        """Get a conversation by ID."""
        conversation_dao = ConversationDAO(self._session)
        conversation = conversation_dao.get_by_id(conversation_id)
        if conversation:
            return ConversationModel.model_validate(conversation)
        return None

    def get_conversation_by_id(self, conversation_id: str, user_id: int) -> Optional[ConversationModel]:
        """Get a conversation by conversation_id and user_id."""
        conversation_dao = ConversationDAO(self._session)
        conversation = conversation_dao.get_by_conversation_id(conversation_id, user_id)
        if conversation:
            return ConversationModel.model_validate(conversation)
        return None

    def list_user_conversations(self, user_id: int) -> List[ConversationModel]:
        """List all conversations for a user."""
        conversation_dao = ConversationDAO(self._session)
        conversations = conversation_dao.list_by_user(user_id)
        return [ConversationModel.model_validate(conv) for conv in conversations]

    def create_conversation(
        self, user_id: int, conversation_id: str, has_uploaded_file: bool = False
    ) -> ConversationModel:
        """Create a new conversation."""
        conversation_dao = ConversationDAO(self._session)
        conversation = conversation_dao.create(user_id, conversation_id, has_uploaded_file)
        return ConversationModel.model_validate(conversation)

    def update_conversation(self, id: int, has_uploaded_file: bool) -> Optional[ConversationModel]:
        """Update an existing conversation."""
        conversation_dao = ConversationDAO(self._session)
        conversation = conversation_dao.update(id, has_uploaded_file)
        if conversation:
            return ConversationModel.model_validate(conversation)
        return None

    def delete_conversation(self, id: int) -> bool:
        """Delete a conversation."""
        conversation_dao = ConversationDAO(self._session)
        return conversation_dao.delete(id)
