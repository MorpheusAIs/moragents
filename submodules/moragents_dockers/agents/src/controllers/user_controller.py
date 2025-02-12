import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from src.models.session import DBSessionFactory
from src.models.daos.user_dao import UserDAO
from src.models.service.service_models import UserModel

logger = logging.getLogger(__name__)


class UserController:
    """Controller for managing users."""

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

    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get a user by ID."""
        user_dao = UserDAO(self._session)
        user = user_dao.get_by_id(user_id)
        if user:
            return UserModel.model_validate(user)
        return None

    def get_user_by_wallet(self, wallet_address: str) -> Optional[UserModel]:
        """Get a user by wallet address."""
        user_dao = UserDAO(self._session)
        user = user_dao.get_by_wallet_address(wallet_address)
        if user:
            return UserModel.model_validate(user)
        return None

    def list_users(self) -> List[UserModel]:
        """List all users."""
        user_dao = UserDAO(self._session)
        users = user_dao.list_all()
        return [UserModel.model_validate(user) for user in users]

    def create_user(self, wallet_address: str) -> UserModel:
        """Create a new user."""
        user_dao = UserDAO(self._session)
        user = user_dao.create(wallet_address)
        return UserModel.model_validate(user)

    def update_user(self, user_id: int, wallet_address: str) -> Optional[UserModel]:
        """Update an existing user."""
        user_dao = UserDAO(self._session)
        user = user_dao.update(user_id, wallet_address)
        if user:
            return UserModel.model_validate(user)
        return None

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user_dao = UserDAO(self._session)
        return user_dao.delete(user_id)
