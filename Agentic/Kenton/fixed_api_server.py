#!/usr/bin/env python3
"""
API server for Deep Research Agent with improved error handling and diagnostics.
Provides streaming responses and comprehensive health checks.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()
env_file = script_dir / ".env"

# Make sure we're using the local .env file
if not env_file.exists():
    logger.error(f"ERROR: .env file not found at {env_file}")
    sys.exit(1)

# Only clean truly problematic environment variables
for key in list(os.environ.keys()):
    if key.startswith("OPENAI_") and key != "OPENAI_API_KEY":
        # Remove if it contains problematic characters
        value = os.environ.get(key, "")
        if "…" in value or "\u2026" in value:
            logger.info(f"Removing problematic {key}: {value[:20]}...")
            del os.environ[key]

# Special handling for API key - keep it unless corrupted
if "OPENAI_API_KEY" in os.environ:
    api_key = os.environ["OPENAI_API_KEY"]
    if "…" in api_key or "\u2026" in api_key:
        logger.info(f"Removing corrupted OPENAI_API_KEY")
        del os.environ["OPENAI_API_KEY"]

# Load environment from .env file
from dotenv import load_dotenv
load_dotenv(env_file, override=True)

# Verify we have a valid API key
api_key = os.getenv("OPENAI_API_KEY", "")

# Check for valid API key formats:
# 1. Standard keys (start with 'sk-' and are ~51 chars)
# 2. Project-scoped keys (start with 'sk-proj-' and can be longer)
is_valid_key = (
    (api_key.startswith("sk-") and len(api_key) >= 40) or
    (api_key.startswith("sk-proj-") and len(api_key) >= 60)
)

if not api_key or not is_valid_key:
    logger.error(f"ERROR: Invalid OPENAI_API_KEY loaded (format or length issue, length: {len(api_key)})")
    sys.exit(1)

logger.info(f"Using API key from .env: {api_key[:15]}... (verified length: {len(api_key)})")

# Import after environment is set up
from agent_config import get_agent
from agents import Runner

app = FastAPI(title="Research Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchQuery(BaseModel):
    query: str
    model: str = "gpt-4.1"  # Default model

@app.post("/api/research")
async def research(request: ResearchQuery):
    """Process a research query with enhanced debugging"""
    async def generate():
        try:
            # Initialize agent with model
            logger.info(f"Initializing agent with {request.model}...")
            agent = get_agent(model=request.model)
            
            # Log available tools
            logger.info(f"Agent has {len(agent.tools)} tools available")
            for i, tool in enumerate(agent.tools):
                tool_name = getattr(tool, '__name__', getattr(tool, 'name', str(tool)))
                logger.info(f"  Tool {i+1}: {tool_name}")
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting research...'})}\n\n"
            
            # Run the agent
            logger.info(f"Running query: {request.query}")
            result = await Runner.run(agent, request.query)
            
            # Extract the final output
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            logger.info(f"Got result: {content[:100]}...")
            
            # Stream the content in chunks
            chunk_size = 100
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"Error: {e}")
            logger.error(error_detail)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/health")
async def health():
    """Provides health status and available tools"""
    try:
        agent = get_agent(model="gpt-4.1")
        tool_count = len(agent.tools)
        tool_names = [getattr(tool, '__name__', str(tool)) for tool in agent.tools]
        
        return {
            "status": "healthy",
            "message": "Research agent API is running",
            "tools": {
                "count": tool_count,
                "names": tool_names[:5]  # Show first 5 tools
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    logger.info("Starting research agent API...")
    uvicorn.run(app, host="0.0.0.0", port=8001)