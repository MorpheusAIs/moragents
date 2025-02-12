import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from src.models.session import DBSessionFactory
from src.models.daos.chat_message_dao import ChatMessageDAO
from src.models.service.service_models import ChatMessageModel

logger = logging.getLogger(__name__)


class ChatMessageController:
    """Controller for managing chat messages."""

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

    def get_message(self, message_id: int) -> Optional[ChatMessageModel]:
        """Get a message by ID."""
        message_dao = ChatMessageDAO(self._session)
        message = message_dao.get_by_id(message_id)
        if message:
            return ChatMessageModel.model_validate(message)
        return None

    def list_conversation_messages(
        self, conversation_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ChatMessageModel]:
        """List all messages in a conversation with pagination."""
        message_dao = ChatMessageDAO(self._session)
        messages = message_dao.list_by_conversation(conversation_id, limit, offset)
        return [ChatMessageModel.model_validate(msg) for msg in messages]

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        error_message: Optional[str] = None,
        message_metadata: Optional[Dict[str, Any]] = None,
        requires_action: bool = False,
        action_type: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> ChatMessageModel:
        """Create a new message."""
        message_dao = ChatMessageDAO(self._session)
        message = message_dao.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            error_message=error_message,
            message_metadata=message_metadata,
            requires_action=requires_action,
            action_type=action_type,
            timestamp=timestamp,
        )
        return ChatMessageModel.model_validate(message)

    def update_message(
        self,
        message_id: int,
        content: Optional[str] = None,
        error_message: Optional[str] = None,
        message_metadata: Optional[Dict[str, Any]] = None,
        requires_action: Optional[bool] = None,
        action_type: Optional[str] = None,
    ) -> Optional[ChatMessageModel]:
        """Update an existing message."""
        message_dao = ChatMessageDAO(self._session)
        message = message_dao.update(
            message_id=message_id,
            content=content,
            error_message=error_message,
            message_metadata=message_metadata,
            requires_action=requires_action,
            action_type=action_type,
        )
        if message:
            return ChatMessageModel.model_validate(message)
        return None

    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        message_dao = ChatMessageDAO(self._session)
        return message_dao.delete(message_id)
