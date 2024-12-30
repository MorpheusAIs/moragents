import time
from typing import List, Optional, Dict, Any
from fastapi import Query
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Enhanced chat message model that includes all agent response fields"""

    role: str
    content: str
    agentName: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    requires_action: Optional[bool] = False
    action_type: Optional[str] = None
    timestamp: Optional[float] = Field(default_factory=lambda: time.time())

    def from_agent_response(self, response: "AgentResponse", agent_name: str) -> "ChatMessage":
        """Create a ChatMessage from an AgentResponse"""
        return ChatMessage(
            role="assistant",
            content=response.content,
            agentName=agent_name,
            error_message=response.error_message,
            metadata=response.metadata,
            requires_action=response.requires_action,
            action_type=response.action_type,
        )


class ChatRequest(BaseModel):
    prompt: ChatMessage
    chain_id: str
    wallet_address: str
    conversation_id: str = Query(default="default")


class Conversation(BaseModel):
    messages: List[ChatMessage]
    has_uploaded_file: bool = False


class AgentResponse(BaseModel):
    """Base response model for all agent responses"""

    content: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    requires_action: Optional[bool] = False
    action_type: Optional[str] = None

    def to_chat_message(self, agent_name: str) -> ChatMessage:
        """Convert AgentResponse to ChatMessage"""
        return ChatMessage(
            role="assistant",
            content=self.content,
            agentName=agent_name,
            error_message=self.error_message,
            metadata=self.metadata,
            requires_action=self.requires_action,
            action_type=self.action_type,
        )

    @classmethod
    def success(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> "AgentResponse":
        """Create a successful response"""
        return cls(content=content, metadata=metadata or {})

    @classmethod
    def error(cls, error_message: str) -> "AgentResponse":
        """Create an error response"""
        return cls(content="An error occurred", error_message=error_message)

    @classmethod
    def action_required(
        cls, content: str, action_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> "AgentResponse":
        """Create a response that requires user action"""
        return cls(content=content, requires_action=True, action_type=action_type, metadata=metadata or {})
