from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.core.user_models import User


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
