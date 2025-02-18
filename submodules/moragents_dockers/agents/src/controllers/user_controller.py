import logging
from typing import Optional, List, Dict, Any, Self

from sqlalchemy.orm import Session

from src.models.session import DBSessionFactory
from src.models.daos.user_dao import UserDAO
from src.models.service.user_models import UserModel, UserSettingModel

logger = logging.getLogger(__name__)


class UserController:
    """Controller for managing users and user settings."""

    def __init__(self, session: Optional[Session] = None, auto_close_session: Optional[bool] = None):
        self._auto_close_session = (session is None) if (auto_close_session is None) else auto_close_session
        self._session: Optional[Session] = session

    def __enter__(self) -> Self:
        """Context manager entry point."""
        if self._session is None:
            self._session = DBSessionFactory.get_instance().new_session()
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[Exception], traceback: Optional[Any]) -> None:
        """Context manager exit point."""
        if self._auto_close_session and self._session:
            self._session.close()

    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get a user by ID."""
        if not self._session:
            return None
        user_dao = UserDAO(self._session)
        user = user_dao.get_by_id(user_id)
        if user:
            return UserModel.model_validate(user)
        return None

    def get_user_by_wallet(self, wallet_address: str) -> Optional[UserModel]:
        """Get a user by wallet address."""
        if not self._session:
            return None
        user_dao = UserDAO(self._session)
        user = user_dao.get_by_wallet_address(wallet_address)
        if user:
            return UserModel.model_validate(user)
        return None

    def list_users(self) -> List[UserModel]:
        """List all users."""
        if not self._session:
            return []
        user_dao = UserDAO(self._session)
        users = user_dao.list_all()
        return [UserModel.model_validate(user) for user in users]

    def create_user(self, wallet_address: str) -> UserModel:
        """Create a new user."""
        if not self._session:
            raise RuntimeError("No database session available")
        user_dao = UserDAO(self._session)
        user = user_dao.create(wallet_address)
        return UserModel.model_validate(user)

    def update_user(self, user_id: int, wallet_address: str) -> Optional[UserModel]:
        """Update an existing user."""
        if not self._session:
            return None
        user_dao = UserDAO(self._session)
        user = user_dao.update(user_id, wallet_address)
        if user:
            return UserModel.model_validate(user)
        return None

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        if not self._session:
            return False
        user_dao = UserDAO(self._session)
        return user_dao.delete(user_id)

    # User Settings Methods
    def get_setting(self, user_id: int, settings_key: str) -> Optional[UserSettingModel]:
        """Get a setting by key for a specific user."""
        if not self._session:
            return None
        user_dao = UserDAO(self._session)
        setting = user_dao.get_setting(user_id, settings_key)
        if setting:
            return UserSettingModel.model_validate(setting)
        return None

    def list_user_settings(self, user_id: int) -> List[UserSettingModel]:
        """List all settings for a user."""
        if not self._session:
            return []
        user_dao = UserDAO(self._session)
        settings = user_dao.get_all_settings(user_id)
        return [UserSettingModel.model_validate(setting) for setting in settings]

    def create_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSettingModel:
        """Create a new setting."""
        if not self._session:
            raise RuntimeError("No database session available")
        user_dao = UserDAO(self._session)
        setting = user_dao.create_setting(user_id, settings_key, settings_value)
        return UserSettingModel.model_validate(setting)

    def update_setting(
        self, user_id: int, settings_key: str, settings_value: Dict[str, Any]
    ) -> Optional[UserSettingModel]:
        """Update an existing setting."""
        if not self._session:
            return None
        user_dao = UserDAO(self._session)
        setting = user_dao.update_setting(user_id, settings_key, settings_value)
        if setting:
            return UserSettingModel.model_validate(setting)
        return None

    def upsert_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSettingModel:
        """Create or update a setting."""
        if not self._session:
            raise RuntimeError("No database session available")
        user_dao = UserDAO(self._session)
        setting = user_dao.upsert_setting(user_id, settings_key, settings_value)
        return UserSettingModel.model_validate(setting)

    def delete_setting(self, user_id: int, settings_key: str) -> bool:
        """Delete a setting."""
        if not self._session:
            return False
        user_dao = UserDAO(self._session)
        return user_dao.delete_setting(user_id, settings_key)
