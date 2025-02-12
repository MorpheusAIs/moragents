import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from src.models.session import DBSessionFactory
from src.models.daos.user_setting_dao import UserSettingDAO
from src.models.service.service_models import UserSettingModel

logger = logging.getLogger(__name__)


class UserSettingController:
    """Controller for managing user settings."""

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

    def get_setting(self, setting_id: int) -> Optional[UserSettingModel]:
        """Get a setting by ID."""
        setting_dao = UserSettingDAO(self._session)
        setting = setting_dao.get_by_id(setting_id)
        if setting:
            return UserSettingModel.model_validate(setting)
        return None

    def get_setting_by_key(self, user_id: int, settings_key: str) -> Optional[UserSettingModel]:
        """Get a setting by key for a specific user."""
        setting_dao = UserSettingDAO(self._session)
        setting = setting_dao.get_by_key(user_id, settings_key)
        if setting:
            return UserSettingModel.model_validate(setting)
        return None

    def list_user_settings(self, user_id: int) -> List[UserSettingModel]:
        """List all settings for a user."""
        setting_dao = UserSettingDAO(self._session)
        settings = setting_dao.list_by_user(user_id)
        return [UserSettingModel.model_validate(setting) for setting in settings]

    def create_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSettingModel:
        """Create a new setting."""
        setting_dao = UserSettingDAO(self._session)
        setting = setting_dao.create(user_id, settings_key, settings_value)
        return UserSettingModel.model_validate(setting)

    def update_setting(
        self, user_id: int, settings_key: str, settings_value: Dict[str, Any]
    ) -> Optional[UserSettingModel]:
        """Update an existing setting."""
        setting_dao = UserSettingDAO(self._session)
        setting = setting_dao.update(user_id, settings_key, settings_value)
        if setting:
            return UserSettingModel.model_validate(setting)
        return None

    def upsert_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSettingModel:
        """Create or update a setting."""
        setting_dao = UserSettingDAO(self._session)
        setting = setting_dao.upsert(user_id, settings_key, settings_value)
        return UserSettingModel.model_validate(setting)

    def delete_setting(self, setting_id: int) -> bool:
        """Delete a setting by ID."""
        setting_dao = UserSettingDAO(self._session)
        return setting_dao.delete(setting_id)

    def delete_setting_by_key(self, user_id: int, settings_key: str) -> bool:
        """Delete a setting by key for a specific user."""
        setting_dao = UserSettingDAO(self._session)
        return setting_dao.delete_by_key(user_id, settings_key)
