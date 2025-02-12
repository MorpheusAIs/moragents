from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import DateTime, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.core.user_setting_models import UserSetting
    from src.models.core.conversation_models import Conversation


class User(Base):
    """SQLAlchemy model for users"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    settings: Mapped[List["UserSetting"]] = relationship(
        "UserSetting", back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
