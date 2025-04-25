"""
Chat Router
---------

Router handling chat-related endpoints including message sending and history.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage import registry_factory

router = APIRouter()

class ChatMessage(BaseModel):
    """Schema for chat messages."""
    role: str
    content: str
    timestamp: Optional[str] = None

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
    
    if not await registry.exists(chat_request.agent_name):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    runner = runner_factory(stream=chat_request.stream)
    
    try:
        # Get response from agent
        response = await runner.run(agent, chat_request.message)
        
        # Format chat history
        messages = [
            ChatMessage(role="user", content=chat_request.message),
            ChatMessage(role="assistant", content=response)
        ]
        
        return {
            "agent_name": chat_request.agent_name,
            "response": response,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_chat(chat_request: ChatRequest) -> StreamingResponse:
    """Stream chat responses from an agent."""
    if not chat_request.stream:
        raise HTTPException(status_code=400, detail="Streaming must be enabled for this endpoint")
    
    registry = registry_factory()
    
    if not await registry.exists(chat_request.agent_name):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    runner = runner_factory(stream=True)
    
    async def event_generator():
        async for chunk in runner.stream(agent, chat_request.message):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/{agent_name}/history", response_model=List[ChatMessage])
async def get_chat_history(agent_name: str) -> List[Dict[str, Any]]:
    """Get chat history for an agent."""
    registry = registry_factory()
    
    if not await registry.exists(agent_name):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # This would need to be implemented in the storage backend
    # For now, return empty list
    return [] 
