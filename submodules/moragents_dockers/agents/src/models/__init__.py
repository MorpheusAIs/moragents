"""Models package."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata

from src.models.core.user_models import User, UserSetting

__all__ = ["Base", "User", "UserSetting"]
