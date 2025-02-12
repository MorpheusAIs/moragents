# pylint: disable=not-callable

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, String, Integer, ForeignKey, func, Boolean, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.core.conversation_models import Conversation


class ChatMessage(Base):
    """SQLAlchemy model for chat messages"""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_metadata: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True, default=dict)
    requires_action: Mapped[bool] = mapped_column(Boolean, default=False)
    action_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
