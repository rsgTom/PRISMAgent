"""
Tests for the chat storage functionality.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import List

from PRISMAgent.storage.chat_storage import ChatMessage, BaseChatStorage
from PRISMAgent.storage.in_memory_chat_storage import InMemoryChatStorage
from PRISMAgent.storage import chat_storage_factory


@pytest.fixture
def chat_storage() -> BaseChatStorage:
    """Get an instance of the in-memory chat storage for testing."""
    # Reset the in-memory store before each test
    InMemoryChatStorage._store.clear()
    return InMemoryChatStorage()


@pytest.mark.asyncio
async def test_save_and_retrieve_message(chat_storage: BaseChatStorage):
    """Test saving and retrieving a single message."""
    # Arrange
    agent_name = "test_agent"
    message = ChatMessage(role="user", content="Hello, world!")
    
    # Act
    await chat_storage.save_message(agent_name, message)
    history = await chat_storage.get_history(agent_name)
    
    # Assert
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Hello, world!"
    assert history[0].timestamp is not None


@pytest.mark.asyncio
async def test_retrieve_empty_history(chat_storage: BaseChatStorage):
    """Test retrieving history for an agent with no messages."""
    # Act
    history = await chat_storage.get_history("nonexistent_agent")
    
    # Assert
    assert isinstance(history, list)
    assert len(history) == 0


@pytest.mark.asyncio
async def test_retrieve_with_limit(chat_storage: BaseChatStorage):
    """Test retrieving history with a limit."""
    # Arrange
    agent_name = "test_agent"
    
    # Create messages with timestamps 5 minutes apart
    for i in range(10):
        timestamp = (datetime.utcnow() - timedelta(minutes=i*5)).isoformat()
        message = ChatMessage(role="user", content=f"Message {i}", timestamp=timestamp)
        await chat_storage.save_message(agent_name, message)
    
    # Act - Get the most recent 5 messages
    history = await chat_storage.get_history(agent_name, limit=5)
    
    # Assert
    assert len(history) == 5
    # The messages should be in chronological order (oldest first)
    assert history[0].content == "Message 9"  # Oldest message (based on our timestamps)
    assert history[4].content == "Message 0"  # Most recent message


@pytest.mark.asyncio
async def test_clear_history(chat_storage: BaseChatStorage):
    """Test clearing the history for an agent."""
    # Arrange
    agent_name = "test_agent"
    await chat_storage.save_message(agent_name, ChatMessage(role="user", content="Hello"))
    await chat_storage.save_message(agent_name, ChatMessage(role="assistant", content="Hi there"))
    
    # Verify messages were saved
    history_before = await chat_storage.get_history(agent_name)
    assert len(history_before) == 2
    
    # Act
    await chat_storage.clear_history(agent_name)
    
    # Assert
    history_after = await chat_storage.get_history(agent_name)
    assert len(history_after) == 0


@pytest.mark.asyncio
async def test_multiple_agents(chat_storage: BaseChatStorage):
    """Test that histories for different agents are kept separate."""
    # Arrange
    agent1 = "agent1"
    agent2 = "agent2"
    
    # Act
    await chat_storage.save_message(agent1, ChatMessage(role="user", content="Message for agent 1"))
    await chat_storage.save_message(agent2, ChatMessage(role="user", content="Message for agent 2"))
    
    # Assert
    history1 = await chat_storage.get_history(agent1)
    history2 = await chat_storage.get_history(agent2)
    
    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0].content == "Message for agent 1"
    assert history2[0].content == "Message for agent 2"


@pytest.mark.asyncio
async def test_conversation_order(chat_storage: BaseChatStorage):
    """Test that a full conversation is returned in the correct order."""
    # Arrange
    agent_name = "test_agent"
    
    # Create a conversation
    messages = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there! How can I help you?"),
        ChatMessage(role="user", content="I have a question about PRISMAgent"),
        ChatMessage(role="assistant", content="I'd be happy to help with that!")
    ]
    
    # Save messages with proper timestamps to ensure order
    for i, message in enumerate(messages):
        timestamp = (datetime.utcnow() + timedelta(minutes=i)).isoformat()
        message.timestamp = timestamp
        await chat_storage.save_message(agent_name, message)
    
    # Act
    history = await chat_storage.get_history(agent_name)
    
    # Assert
    assert len(history) == 4
    assert [msg.role for msg in history] == ["user", "assistant", "user", "assistant"]
    assert [msg.content for msg in history] == [
        "Hello", 
        "Hi there! How can I help you?", 
        "I have a question about PRISMAgent", 
        "I'd be happy to help with that!"
    ]


@pytest.mark.asyncio
async def test_chat_storage_factory():
    """Test that the chat storage factory returns the expected instance."""
    # Act
    storage = chat_storage_factory(storage_type="memory")
    
    # Assert
    assert isinstance(storage, InMemoryChatStorage)
    
    # Clean up
    InMemoryChatStorage._store.clear()


@pytest.mark.asyncio
async def test_factory_singleton():
    """Test that the chat storage factory returns the same instance each time."""
    # Act
    storage1 = chat_storage_factory()
    storage2 = chat_storage_factory()
    
    # Assert
    assert storage1 is storage2

    # Clean up
    InMemoryChatStorage._store.clear()
