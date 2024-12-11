from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: ChatMessage
    chain_id: str
    wallet_address: str


class ChatMessage(BaseModel):
    role: str
    content: str
    agentName: Optional[str] = None


class Conversation(BaseModel):
    messages: List[ChatMessage]
    has_uploaded_file: bool = False
