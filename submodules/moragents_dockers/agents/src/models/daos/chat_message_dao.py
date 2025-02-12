from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.core.chat_message_models import ChatMessage


class ChatMessageDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        error_message: Optional[str] = None,
        message_metadata: Optional[Dict[str, Any]] = None,
        requires_action: bool = False,
        action_type: Optional[str] = None,
        timestamp: float = None,
    ) -> ChatMessage:
        if timestamp is None:
            timestamp = datetime.utcnow().timestamp()

        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            error_message=error_message,
            message_metadata=message_metadata or {},
            requires_action=requires_action,
            action_type=action_type,
            timestamp=timestamp,
        )
        self.session.add(message)
        self.session.commit()
        return message

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        return self.session.get(ChatMessage, message_id)

    def list_by_conversation(
        self, conversation_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.timestamp.asc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        return list(self.session.execute(stmt).scalars())

    def update(
        self,
        message_id: int,
        content: Optional[str] = None,
        error_message: Optional[str] = None,
        message_metadata: Optional[Dict[str, Any]] = None,
        requires_action: Optional[bool] = None,
        action_type: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        message = self.get_by_id(message_id)
        if message:
            if content is not None:
                message.content = content
            if error_message is not None:
                message.error_message = error_message
            if message_metadata is not None:
                message.message_metadata = message_metadata
            if requires_action is not None:
                message.requires_action = requires_action
            if action_type is not None:
                message.action_type = action_type
            message.updated_at = datetime.utcnow()
            self.session.commit()
        return message

    def delete(self, message_id: int) -> bool:
        message = self.get_by_id(message_id)
        if message:
            self.session.delete(message)
            self.session.commit()
            return True
        return False
