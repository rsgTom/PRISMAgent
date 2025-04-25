"""
Chat Router
----------

Router handling chat-related endpoints including message sending and history.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage import registry_factory, chat_storage_factory
from PRISMAgent.storage.chat_storage import ChatMessage
from PRISMAgent.util import get_logger

# Get a logger for this module
logger = get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    """Schema for chat requests."""
    agent_name: str
    message: str
    stream: bool = False

class ChatResponse(BaseModel):
    """Schema for chat responses."""
    agent_name: str
    response: str
    messages: List[ChatMessage]

@router.post("/send", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest) -> Dict[str, Any]:
    """Send a message to an agent and get a response."""
    registry = registry_factory()
    chat_storage = chat_storage_factory()
    
    if not await registry.exists(chat_request.agent_name):
        logger.warning(f"Agent not found: {chat_request.agent_name}")
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    runner = runner_factory(stream=chat_request.stream)
    
    try:
        # Get response from agent
        response = await runner.run(agent, chat_request.message)
        
        # Create chat messages
        user_message = ChatMessage(role="user", content=chat_request.message)
        assistant_message = ChatMessage(role="assistant", content=response)
        
        # Save messages to chat history
        await chat_storage.save_message(chat_request.agent_name, user_message)
        await chat_storage.save_message(chat_request.agent_name, assistant_message)
        
        # Get recent messages for response
        messages = await chat_storage.get_history(chat_request.agent_name, limit=10)
        
        logger.info(f"Chat message processed for agent: {chat_request.agent_name}",
                   agent_name=chat_request.agent_name,
                   message_length=len(chat_request.message),
                   response_length=len(response))
        
        return {
            "agent_name": chat_request.agent_name,
            "response": response,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}",
                    agent_name=chat_request.agent_name,
                    error=str(e),
                    exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_chat(chat_request: ChatRequest) -> StreamingResponse:
    """Stream chat responses from an agent."""
    if not chat_request.stream:
        raise HTTPException(status_code=400, detail="Streaming must be enabled for this endpoint")
    
    registry = registry_factory()
    chat_storage = chat_storage_factory()
    
    if not await registry.exists(chat_request.agent_name):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    runner = runner_factory(stream=True)
    
    # Save the user message to chat history
    user_message = ChatMessage(role="user", content=chat_request.message)
    await chat_storage.save_message(chat_request.agent_name, user_message)
    
    async def event_generator():
        full_response = ""
        
        async for chunk in runner.stream(agent, chat_request.message):
            full_response += chunk
            yield f"data: {chunk}\n\n"
            
        # Save the complete assistant response to chat history
        assistant_message = ChatMessage(role="assistant", content=full_response)
        await chat_storage.save_message(chat_request.agent_name, assistant_message)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/{agent_name}/history", response_model=List[ChatMessage])
async def get_chat_history(agent_name: str, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
    """Get chat history for an agent.
    
    Parameters:
    -----------
    agent_name : str
        The name of the agent to get history for
    limit : int, optional
        Maximum number of messages to return (default: 50)
    """
    registry = registry_factory()
    chat_storage = chat_storage_factory()
    
    if not await registry.exists(agent_name):
        logger.warning(f"Agent not found when requesting history: {agent_name}")
        raise HTTPException(status_code=404, detail="Agent not found")
    
    logger.info(f"Retrieving chat history for agent: {agent_name}", 
               agent_name=agent_name, limit=limit)
    
    # Get chat history from storage
    messages = await chat_storage.get_history(agent_name, limit=limit)
    
    return messages

@router.delete("/{agent_name}/history")
async def clear_chat_history(agent_name: str) -> Dict[str, Any]:
    """Clear chat history for an agent."""
    registry = registry_factory()
    chat_storage = chat_storage_factory()
    
    if not await registry.exists(agent_name):
        logger.warning(f"Agent not found when clearing history: {agent_name}")
        raise HTTPException(status_code=404, detail="Agent not found")
    
    logger.info(f"Clearing chat history for agent: {agent_name}", agent_name=agent_name)
    
    # Clear chat history from storage
    await chat_storage.clear_history(agent_name)
    
    return {"status": "success", "message": f"Chat history cleared for {agent_name}"}
