"""
PRISMAgent FastAPI Application
----------------------------

Main FastAPI application entry point with router configuration and middleware setup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any

from PRISMAgent.config import OPENAI_API_KEY
from PRISMAgent.ui.api.routers import agents, chat, tools

# Initialize FastAPI app
app = FastAPI(
    title="PRISMAgent API",
    description="REST API for PRISMAgent - A modular, multi-agent framework",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])

@app.get("/", response_model=Dict[str, Any])
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information."""
    return {
        "name": "PRISMAgent API",
        "version": "0.1.0",
        "status": "operational",
        "docs_url": "/docs",
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    if not OPENAI_API_KEY:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "OpenAI API key not configured"}
        )
    return {"status": "healthy"} 