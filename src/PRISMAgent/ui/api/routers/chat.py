"""
Chat Router
-----------

Router handling chat-related endpoints including message sending and history.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.storage import registry_factory
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

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
@with_log_context(component="chat_api")
async def send_message(chat_request: ChatRequest) -> Dict[str, Any]:
    """Send a message to an agent and get a response."""
    logger.info(f"Received chat request for agent: {chat_request.agent_name}", 
               agent_name=chat_request.agent_name,
               message_length=len(chat_request.message),
               stream=chat_request.stream)
    
    registry = registry_factory()
    
    if not await registry.exists(chat_request.agent_name):
        logger.warning(f"Agent not found: {chat_request.agent_name}", 
                      agent_name=chat_request.agent_name)
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    logger.debug(f"Retrieved agent: {chat_request.agent_name}", 
                agent_name=chat_request.agent_name)
    
    runner = runner_factory(stream=chat_request.stream)
    
    try:
        # Get response from agent
        logger.debug(f"Running agent {chat_request.agent_name} with message", 
                    agent_name=chat_request.agent_name,
                    message_length=len(chat_request.message))
        
        response = await runner.run(agent, chat_request.message)
        
        logger.debug(f"Received response from agent {chat_request.agent_name}", 
                    agent_name=chat_request.agent_name,
                    response_length=len(response))
        
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
        logger.error(f"Error processing chat request: {str(e)}", 
                    agent_name=chat_request.agent_name, 
                    error=str(e), 
                    exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
@with_log_context(component="chat_api_stream")
async def stream_chat(chat_request: ChatRequest) -> StreamingResponse:
    """Stream chat responses from an agent."""
    logger.info(f"Received streaming chat request for agent: {chat_request.agent_name}",
               agent_name=chat_request.agent_name,
               message_length=len(chat_request.message))
    
    if not chat_request.stream:
        logger.warning("Stream endpoint called without streaming enabled",
                      agent_name=chat_request.agent_name)
        raise HTTPException(status_code=400, detail="Streaming must be enabled for this endpoint")
    
    registry = registry_factory()
    
    if not await registry.exists(chat_request.agent_name):
        logger.warning(f"Agent not found: {chat_request.agent_name}", 
                      agent_name=chat_request.agent_name)
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = await registry.get_agent(chat_request.agent_name)
    logger.debug(f"Retrieved agent for streaming: {chat_request.agent_name}", 
                agent_name=chat_request.agent_name)
    
    runner = runner_factory(stream=True)
    
    async def event_generator():
        chunk_count = 0
        try:
            async for chunk in runner.stream(agent, chat_request.message):
                chunk_count += 1
                yield f"data: {chunk}\n\n"
            
            logger.debug(f"Streaming completed: {chunk_count} chunks sent", 
                        agent_name=chat_request.agent_name,
                        chunk_count=chunk_count)
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", 
                        agent_name=chat_request.agent_name,
                        error=str(e),
                        exc_info=True)
            # In a streaming response, we can't throw an exception after we've started
            # sending data, so we'll just log the error and end the stream
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/{agent_name}/history", response_model=List[ChatMessage])
@with_log_context(component="chat_history")
async def get_chat_history(agent_name: str) -> List[Dict[str, Any]]:
    """Get chat history for an agent."""
    logger.info(f"Retrieving chat history for agent: {agent_name}", 
               agent_name=agent_name)
    
    registry = registry_factory()
    
    if not await registry.exists(agent_name):
        logger.warning(f"Agent not found when retrieving history: {agent_name}", 
                      agent_name=agent_name)
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # This would need to be implemented in the storage backend
    logger.debug(f"Chat history retrieval attempted for {agent_name} but not implemented", 
                agent_name=agent_name)
    
    # For now, return empty list
    return [] 
