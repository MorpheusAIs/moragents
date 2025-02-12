from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class UserModel(BaseModel):
    id: Optional[int] = None
    wallet_address: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationModel(BaseModel):
    id: Optional[int] = None
    conversation_id: str
    user_id: int
    has_uploaded_file: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatMessageModel(BaseModel):
    id: Optional[int] = None
    conversation_id: int
    role: str
    content: str
    agent_name: Optional[str] = None
    error_message: Optional[str] = None
    message_metadata: Optional[Dict[str, Any]] = None
    requires_action: bool = False
    action_type: Optional[str] = None
    timestamp: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserSettingModel(BaseModel):
    id: Optional[int] = None
    user_id: int
    settings_key: str
    settings_value: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
