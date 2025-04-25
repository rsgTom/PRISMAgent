"""
PRISMAgent.storage.in_memory_chat_storage
----------------------------------------

In-memory implementation of chat history storage.
For production use, consider using a persistent backend.
"""

from typing import Dict, List, Optional, ClassVar
from .chat_storage import BaseChatStorage, ChatMessage


class InMemoryChatStorage(BaseChatStorage):
    """
    In-memory implementation of chat history storage.
    
    Warning: All chat history is lost when the process restarts.
    Use only for development and testing.
    """
    
    _store: ClassVar[Dict[str, List[ChatMessage]]] = {}
    
    async def save_message(self, agent_name: str, message: ChatMessage) -> None:
        """Save a chat message to history."""
        if agent_name not in self._store:
            self._store[agent_name] = []
            
        self._store[agent_name].append(message)
    
    async def get_history(self, agent_name: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get chat history for an agent.
        
        Args:
            agent_name: The name of the agent to retrieve history for
            limit: Optional maximum number of messages to return
            
        Returns:
            List[ChatMessage]: List of chat messages, ordered by timestamp (newest last)
        """
        if agent_name not in self._store:
            return []
            
        messages = self._store[agent_name]
        
        # Sort by timestamp to ensure correct order
        messages = sorted(messages, key=lambda m: m.timestamp)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            messages = messages[-limit:]
            
        return messages
    
    async def clear_history(self, agent_name: str) -> None:
        """Clear chat history for an agent."""
        if agent_name in self._store:
            self._store[agent_name] = []
