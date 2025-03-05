from abc import ABC, abstractmethod
from dataclasses import dataclass


from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from agentopera.chatflow.messages import TextMessage
    
# Status enum for better type safety
class MessageStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

# API Request Model
class UserRequest(BaseModel):
    message: str = Field(..., description="The message content from the user")
    user_id: str = Field(..., description="Unique identifier for the user")
    conversation_id: Optional[str] = Field(None, description="Optional conversation identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What's the company's vacation policy?",
                "user_id": "user_123",
                "conversation_id": "conv_456"
            }
        }

class UserResponse(BaseModel):
    message: str = Field(..., description="The response message content")
    status: MessageStatus = Field(..., description="Current status of the message")
    is_final: bool = Field(..., description="Whether this is the final response")
    message_id: str = Field(..., description="The message ID this response is for")
    conversation_id: Optional[str] = Field(None, description="The conversation this response belongs to")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Our vacation policy allows...",
                "status": "completed",
                "is_final": True,
                "message_id": "message_id_123",
                "conversation_id": "conv_456"
            }
        }

# Define the structured output format.
class IntentResponse(BaseModel):
    intent: str

class IntentClassifierBase(ABC):
    @abstractmethod
    async def classify_intent(self, message: str) -> str:
        pass


class AgentRegistryBase(ABC):
    @abstractmethod
    async def get_agent(self, intent: str) -> str:
        pass



@dataclass
class TerminationMessage(TextMessage):
    """A message that is sent from the system to the user, indicating that the conversation has ended."""

    reason: str


@dataclass
class FinalResult(TextMessage):
    """A message sent from the agent to the user, indicating the end of a conversation"""

