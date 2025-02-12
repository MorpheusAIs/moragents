from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.core.user_setting_models import UserSetting


class UserSettingDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSetting:
        setting = UserSetting(user_id=user_id, settings_key=settings_key, settings_value=settings_value)
        self.session.add(setting)
        self.session.commit()
        return setting

    def get_by_id(self, setting_id: int) -> Optional[UserSetting]:
        return self.session.get(UserSetting, setting_id)

    def get_by_key(self, user_id: int, settings_key: str) -> Optional[UserSetting]:
        stmt = select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.settings_key == settings_key)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_user(self, user_id: int) -> List[UserSetting]:
        stmt = select(UserSetting).where(UserSetting.user_id == user_id)
        return list(self.session.execute(stmt).scalars())

    def update(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> Optional[UserSetting]:
        setting = self.get_by_key(user_id, settings_key)
        if setting:
            setting.settings_value = settings_value
            setting.updated_at = datetime.utcnow()
            self.session.commit()
            return setting
        return None

    def upsert(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSetting:
        setting = self.get_by_key(user_id, settings_key)
        if setting:
            setting.settings_value = settings_value
            setting.updated_at = datetime.utcnow()
        else:
            setting = UserSetting(user_id=user_id, settings_key=settings_key, settings_value=settings_value)
            self.session.add(setting)
        self.session.commit()
        return setting

    def delete(self, setting_id: int) -> bool:
        setting = self.get_by_id(setting_id)
        if setting:
            self.session.delete(setting)
            self.session.commit()
            return True
        return False

    def delete_by_key(self, user_id: int, settings_key: str) -> bool:
        setting = self.get_by_key(user_id, settings_key)
        if setting:
            self.session.delete(setting)
            self.session.commit()
            return True
        return False
