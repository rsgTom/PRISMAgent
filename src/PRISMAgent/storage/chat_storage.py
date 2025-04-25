"""
PRISMAgent.storage.chat_storage
------------------------------

Protocol and models for chat history storage and retrieval.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for chat messages."""
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    

class ChatHistory(BaseModel):
    """Schema for chat history."""
    agent_name: str
    messages: List[ChatMessage] = []
    metadata: Dict[str, Any] = {}
    
    
@runtime_checkable
class ChatStorageProtocol(Protocol):
    """Protocol defining the interface for chat history storage."""
    
    async def save_message(self, agent_name: str, message: ChatMessage) -> None:
        """Save a chat message to history."""
        ...
        
    async def get_history(self, agent_name: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get chat history for an agent.
        
        Args:
            agent_name: The name of the agent to retrieve history for
            limit: Optional maximum number of messages to return
            
        Returns:
            List[ChatMessage]: List of chat messages, ordered by timestamp (newest last)
        """
        ...
        
    async def clear_history(self, agent_name: str) -> None:
        """Clear chat history for an agent."""
        ...


class BaseChatStorage(ABC):
    """Abstract base class for chat history storage implementations."""
    
    @abstractmethod
    async def save_message(self, agent_name: str, message: ChatMessage) -> None:
        """Save a chat message to history."""
        ...
        
    @abstractmethod
    async def get_history(self, agent_name: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get chat history for an agent.
        
        Args:
            agent_name: The name of the agent to retrieve history for
            limit: Optional maximum number of messages to return
            
        Returns:
            List[ChatMessage]: List of chat messages, ordered by timestamp (newest last)
        """
        ...
        
    @abstractmethod  
    async def clear_history(self, agent_name: str) -> None:
        """Clear chat history for an agent."""
        ...
