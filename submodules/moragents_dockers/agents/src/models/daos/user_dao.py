from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.core.user_models import User, UserSetting


class UserDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(self, wallet_address: str) -> User:
        user = User(wallet_address=wallet_address)
        self.session.add(user)
        self.session.commit()
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_wallet_address(self, wallet_address: str) -> Optional[User]:
        stmt = select(User).where(User.wallet_address == wallet_address)
        result = self.session.execute(stmt).scalar_one_or_none()
        return result

    def update(self, user_id: int, wallet_address: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.wallet_address = wallet_address
            user.updated_at = datetime.utcnow()
            self.session.commit()
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def list_all(self) -> List[User]:
        stmt = select(User)
        return list(self.session.execute(stmt).scalars())

    # User Settings Methods
    def get_setting(self, user_id: int, settings_key: str) -> Optional[UserSetting]:
        stmt = select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.settings_key == settings_key)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all_settings(self, user_id: int) -> List[UserSetting]:
        stmt = select(UserSetting).where(UserSetting.user_id == user_id)
        return list(self.session.execute(stmt).scalars())

    def create_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSetting:
        setting = UserSetting(user_id=user_id, settings_key=settings_key, settings_value=settings_value)
        self.session.add(setting)
        self.session.commit()
        return setting

    def update_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> Optional[UserSetting]:
        setting = self.get_setting(user_id, settings_key)
        if setting:
            setting.settings_value = settings_value
            setting.updated_at = datetime.utcnow()
            self.session.commit()
            return setting
        return None

    def upsert_setting(self, user_id: int, settings_key: str, settings_value: Dict[str, Any]) -> UserSetting:
        setting = self.get_setting(user_id, settings_key)
        if setting:
            setting.settings_value = settings_value
            setting.updated_at = datetime.utcnow()
        else:
            setting = UserSetting(user_id=user_id, settings_key=settings_key, settings_value=settings_value)
            self.session.add(setting)
        self.session.commit()
        return setting

    def delete_setting(self, user_id: int, settings_key: str) -> bool:
        setting = self.get_setting(user_id, settings_key)
        if setting:
            self.session.delete(setting)
            self.session.commit()
            return True
        return False
