"""
PRISMAgent FastAPI Application
-----------------------------

Main FastAPI application entry point with router configuration and middleware setup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any

from PRISMAgent.config import OPENAI_API_KEY
from PRISMAgent.ui.api.routers import agents, chat, tools
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PRISMAgent API",
    description="REST API for PRISMAgent - A modular, multi-agent framework",
    version="0.1.0",
)

logger.info("Initializing FastAPI application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug("CORS middleware configured")

# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])

logger.debug("API routers registered")

@app.get("/", response_model=Dict[str, Any])
@with_log_context(endpoint="root")
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information."""
    logger.debug("Serving root endpoint")
    return {
        "name": "PRISMAgent API",
        "version": "0.1.0",
        "status": "operational",
        "docs_url": "/docs",
    }

@app.get("/health", response_model=Dict[str, str])
@with_log_context(endpoint="health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    logger.debug("Performing health check")
    
    if not OPENAI_API_KEY:
        logger.error("Health check failed: OpenAI API key not configured")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "OpenAI API key not configured"}
        )
    
    logger.info("Health check passed")
    return {"status": "healthy"}