from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel


class UserSettingModel(BaseModel):
    """Pydantic model for user settings"""

    id: int
    user_id: int
    settings_key: str
    settings_value: Dict
    created_at: datetime
    updated_at: datetime


class ChatMessageModel(BaseModel):
    """Pydantic model for chat messages"""

    id: int
    conversation_id: int
    role: str
    content: str
    agent_name: Optional[str] = None
    error_message: Optional[str] = None
    message_metadata: Optional[Dict] = None
    requires_action: bool = False
    action_type: Optional[str] = None
    timestamp: float
    created_at: datetime
    updated_at: datetime


class ConversationModel(BaseModel):
    """Pydantic model for conversations"""

    id: int
    conversation_id: str
    user_id: int
    has_uploaded_file: bool = False
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageModel] = []


class UserModel(BaseModel):
    """Pydantic model for users"""

    id: int
    wallet_address: str
    created_at: datetime
    updated_at: datetime
    settings: List[UserSettingModel] = []
    conversations: List[ConversationModel] = []
