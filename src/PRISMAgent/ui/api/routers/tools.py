"""
Tools Router
-----------

Router handling tool-related endpoints including listing and execution.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from PRISMAgent.tools import tool_factory
from PRISMAgent.tools.spawn import spawn_agent

router = APIRouter()

class ToolExecuteRequest(BaseModel):
    """Schema for tool execution requests."""
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    """Schema for tool responses."""
    tool_name: str
    result: Any
    error: Optional[str] = None

class ToolSchema(BaseModel):
    """Schema for tool information."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str]

@router.get("/", response_model=List[ToolSchema])
async def list_tools() -> List[Dict[str, Any]]:
    """List all available tools with their schemas."""
    # For now, just return spawn_agent tool as an example
    return [{
        "name": "spawn_agent",
        "description": spawn_agent.__doc__ or "Spawn a new agent",
        "parameters": {
            "agent_type": {"type": "string", "description": "Type of agent to spawn"},
            "task": {"type": "string", "description": "Task for the agent"},
            "system_prompt": {"type": "string", "description": "Custom system prompt"}
        },
        "required_params": ["agent_type", "task"]
    }]

@router.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolExecuteRequest) -> Dict[str, Any]:
    """Execute a specific tool with given parameters."""
    try:
        if request.tool_name == "spawn_agent":
            result = await spawn_agent(**request.parameters)
            return {
                "tool_name": request.tool_name,
                "result": result,
                "error": None
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Tool {request.tool_name} not found"
            )
    except Exception as e:
        return {
            "tool_name": request.tool_name,
            "result": None,
            "error": str(e)
        }

@router.get("/{tool_name}/schema", response_model=ToolSchema)
async def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get the schema for a specific tool."""
    if tool_name == "spawn_agent":
        return {
            "name": "spawn_agent",
            "description": spawn_agent.__doc__ or "Spawn a new agent",
            "parameters": {
                "agent_type": {"type": "string", "description": "Type of agent to spawn"},
                "task": {"type": "string", "description": "Task for the agent"},
                "system_prompt": {"type": "string", "description": "Custom system prompt"}
            },
            "required_params": ["agent_type", "task"]
        }
    raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found") 