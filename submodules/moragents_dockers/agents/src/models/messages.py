from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel


# class ChatMessage(BaseModel):
#     role: str
#     content: str


class ChatMessage(BaseModel):
    role: str
    content: str
    agentName: Optional[str] = None


class ChatRequest(BaseModel):
    prompt: ChatMessage
    chain_id: str
    wallet_address: str
    conversation_id: str = Query(default="default")


class Conversation(BaseModel):
    messages: List[ChatMessage]
    has_uploaded_file: bool = False
