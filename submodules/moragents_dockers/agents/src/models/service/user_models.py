from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class UserModel(BaseModel):
    id: Optional[int] = None
    wallet_address: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserSettingModel(BaseModel):
    id: Optional[int] = None
    user_id: int
    settings_key: str
    settings_value: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
