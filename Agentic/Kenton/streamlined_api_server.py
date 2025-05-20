#!/usr/bin/env python3
"""
Streamlined API server for the Kenton Research Agent
"""

import os
import sys
import json
import asyncio
import traceback
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Try to import uvicorn with fallback message
try:
    import uvicorn
except ImportError:
    print("ERROR: uvicorn not installed. Install with: pip install uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import centralized environment config
from env_config import setup_environment
config = setup_environment()

# Import after environment setup
from agent_config import get_agent
from agents import Runner

app = FastAPI(title="Streamlined Research Agent API")

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
    model: str = "gpt-4.1"

@app.post("/api/research")
async def research(request: ResearchQuery):
    """Process a research query with the agent."""
    async def generate():
        try:
            # Initialize agent with model
            logger.info(f"Initializing agent with {request.model}...")
            agent = get_agent(model=request.model)
            
            # Log tool information
            tool_count = len(agent.tools)
            tool_names = [getattr(tool, '__name__', str(tool)) for tool in agent.tools]
            logger.info(f"Agent has {tool_count} tools: {', '.join(tool_names[:5])}...")
            
            yield f"data: {json.dumps({'type': 'status', 'message': f'Starting research with {tool_count} tools...'})}\n\n"
            
            # Run the agent
            logger.info(f"Running query: {request.query}")
            result = await Runner.run(agent, request.query)
            
            # Extract output
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
                
            logger.info(f"Got result: {content[:100]}...")
            
            # Stream in chunks
            chunk_size = 100
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                await asyncio.sleep(0.01)
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error: {e}")
            logger.error(error_detail)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/api/health")
async def health():
    """Health check endpoint that verifies tools are loaded."""
    try:
        agent = get_agent(model="gpt-4.1")
        tool_count = len(agent.tools)
        tool_names = [getattr(tool, '__name__', str(tool)) for tool in agent.tools]
        
        # Check if specific tools exist
        has_weather = any('weather' in str(name).lower() for name in tool_names)
        has_news = any('news' in str(name).lower() for name in tool_names)
        
        return {
            "status": "healthy",
            "message": "Research agent API is running",
            "tools": {
                "count": tool_count,
                "has_weather": has_weather,
                "has_news": has_news,
                "weather_api_key_configured": bool(os.getenv("WEATHER_API_KEY")),
                "names": tool_names[:5]  # Show first 5 tools
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    logger.info("Starting streamlined API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)