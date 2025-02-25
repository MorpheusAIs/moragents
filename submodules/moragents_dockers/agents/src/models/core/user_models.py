from datetime import datetime
from typing import List

from sqlalchemy import JSON, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class UserSetting(Base):
    """SQLAlchemy model for user settings"""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    settings_key: Mapped[str] = mapped_column(String(255), nullable=False)
    settings_value: Mapped[JSON] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

    __table_args__ = (
        # Ensure unique key per user
        {"unique_constraints": [("user_id", "settings_key")]}
    )


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
