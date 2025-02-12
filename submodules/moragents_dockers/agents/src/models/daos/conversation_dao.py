from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.core.conversation_models import Conversation


class ConversationDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, conversation_id: str, has_uploaded_file: bool = False) -> Conversation:
        conversation = Conversation(
            conversation_id=conversation_id, user_id=user_id, has_uploaded_file=has_uploaded_file
        )
        self.session.add(conversation)
        self.session.commit()
        return conversation

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        return self.session.get(Conversation, conversation_id)

    def get_by_conversation_id(self, conversation_id: str, user_id: int) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.conversation_id == conversation_id, Conversation.user_id == user_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_user(self, user_id: int) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id)
        return list(self.session.execute(stmt).scalars())

    def update(self, id: int, has_uploaded_file: bool) -> Optional[Conversation]:
        conversation = self.get_by_id(id)
        if conversation:
            conversation.has_uploaded_file = has_uploaded_file
            conversation.updated_at = datetime.utcnow()
            self.session.commit()
        return conversation

    def delete(self, id: int) -> bool:
        conversation = self.get_by_id(id)
        if conversation:
            self.session.delete(conversation)
            self.session.commit()
            return True
        return False
