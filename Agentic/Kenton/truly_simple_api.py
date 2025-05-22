#!/usr/bin/env python3
"""
Extremely simple API server that runs the exact same process as run.py
"""

import os
import sys
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()
env_file = script_dir / ".env"

# Make sure we're using the local .env file
if not env_file.exists():
    print(f"ERROR: .env file not found at {env_file}")
    sys.exit(1)

# Clear any problematic OPENAI variables to ensure we use .env
for key in list(os.environ.keys()):
    if key.startswith("OPENAI_"):
        # Remove if it contains problematic characters or is too short
        value = os.environ.get(key, "")
        if "…" in value or "\u2026" in value or (key == "OPENAI_API_KEY" and len(value) < 50):
            print(f"Removing problematic {key}: {value[:20]}...")
            del os.environ[key]

# Load environment from .env file
from dotenv import load_dotenv
load_dotenv(env_file, override=True)

# Verify we have a valid API key
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key or len(api_key) < 50:
    print(f"ERROR: Invalid OPENAI_API_KEY loaded (length: {len(api_key)})")
    sys.exit(1)

print(f"Using API key from .env: {api_key[:15]}... (verified length: {len(api_key)})")

# Import after environment is set up
from agent_config import get_agent
from agents import Runner

app = FastAPI(title="Simple Research Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchQuery(BaseModel):
    query: str
    model: str = "gpt-4.1"  # Default to gpt-4.1 for better availability
    include_api_stats: bool = False  # Whether to include API call stats in response

@app.post("/api/research")
async def research(request: ResearchQuery):
    """Process a research query exactly like run.py does"""
    # Use a simplified approach to track API calls
    api_calls = []
    
    # Track this research session
    session_id = f"research-{int(time.time())}"
    
    async def generate():
        try:
            # Initialize agent with model
            print(f"Initializing agent with {request.model}...")
            agent = get_agent(model=request.model)
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting research...'})}\n\n"
            
            # Record timestamp before running the agent
            start_time = time.time()
            
            # Run the agent
            result = await Runner.run(agent, request.query)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract the final output
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Stream the content in chunks
            chunk_size = 1000  # Increased chunk size to reduce number of messages
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            # Add API stats if requested
            if request.include_api_stats:
                # Just provide basic timing information since we can't get the full stats yet
                api_stats = {
                    "timing": {
                        "duration_ms": round(duration_ms, 2),
                        "query": request.query,
                        "model": request.model
                    }
                }
                
                # Send simplified API stats
                yield f"data: {json.dumps({'type': 'api_stats', 'stats': api_stats})}\n\n"
            
            # Send completion event with timing information
            yield f"data: {json.dumps({
                'type': 'complete',
                'timing': {
                    'duration_ms': round(duration_ms, 2)
                }
            })}\n\n"
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error: {e}")
            print(error_detail)
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
    return {"status": "healthy", "message": "Research agent API is running"}


@app.get("/api/monitor")
async def api_monitor():
    """Get API call monitoring information."""
    try:
        # For now, return placeholder data instead of using the API monitor
        return {
            "stats": {
                "total_calls": 0,
                "active_calls": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "avg_duration_ms": 0,
                "tools": {}
            },
            "recent_calls": [],
            "visualization": {
                "timeline": [
                    {"time": "12:00", "total": 0, "success": 0, "error": 0, "tools": {}}
                ],
                "top_tools": [],
                "top_error_tools": [],
                "status_summary": {"success": 0, "error": 0}
            },
            "message": "API monitoring is available in the UI but not yet collecting data"
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start the research agent API server")
    parser.add_argument("--port", type=int, default=8001, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    args = parser.parse_args()
    
    print(f"Starting truly simple agent API on {args.host}:{args.port}...")
    uvicorn.run(app, host=args.host, port=args.port)