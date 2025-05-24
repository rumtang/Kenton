#!/usr/bin/env python3
"""
API server for Deep Research Agent with improved error handling and diagnostics.
Provides streaming responses, comprehensive health checks, and conversation memory.
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
import uuid

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

# Load environment variables AFTER cleanup
from dotenv import load_dotenv
logger.info(f"Loading .env from: {env_file}")
load_result = load_dotenv(dotenv_path=env_file, override=True)
logger.info(f"Load .env result: {load_result}")

# Import conversation manager
try:
    from conversation_manager import get_conversation_manager
    conversation_manager = get_conversation_manager()
    logger.info("Conversation manager initialized")
except Exception as e:
    logger.warning(f"Could not initialize conversation manager: {e}")
    conversation_manager = None

# Now check for required environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("ERROR: OPENAI_API_KEY not found in environment after loading .env")
    sys.exit(1)

# Validate API key format
if not api_key.startswith("sk-"):
    logger.error(f"ERROR: Invalid OPENAI_API_KEY format")
    sys.exit(1)

logger.info(f"OPENAI_API_KEY loaded: {api_key[:15]}...{api_key[-4:]}")

# Import the agent config
try:
    from agent_config import get_agent, SessionManager
    from tools.enhanced_mcp_wrapper import get_enhanced_mcp_tools
    from tools.tavily_search import tavily_search
    
    # Create session manager instance
    session_manager = SessionManager()
    
    logger.info("Successfully imported agent_config and tools")
except ImportError as e:
    logger.error(f"Failed to import agent_config or tools: {e}")
    sys.exit(1)

app = FastAPI()

def generate_session_id():
    """Generate a unique session ID."""
    return f"session_{uuid.uuid4().hex[:12]}_{int(asyncio.get_event_loop().time())}"

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str
    sessionId: str = None
    includeIntelligence: bool = True
    model: str = "gpt-4.1"

class HealthResponse(BaseModel):
    status: str
    tools_count: int
    agent_ready: bool
    api_key_status: str
    enhanced_mcp_status: str
    tavily_status: str
    memory_status: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with detailed status information."""
    try:
        # Get tools status
        enhanced_mcp_tools = []
        enhanced_mcp_status = "not loaded"
        try:
            mcp_path = os.getenv("MCP_CONFIG_PATH", "./consulting_brain_apis.mcp")
            enhanced_mcp_tools = get_enhanced_mcp_tools(mcp_path)
            enhanced_mcp_status = f"loaded ({len(enhanced_mcp_tools)} tools)"
        except Exception as e:
            enhanced_mcp_status = f"error: {str(e)}"
        
        # Get tavily status
        tavily_status = "not loaded"
        try:
            # Check if Tavily API key is configured
            tavily_key = os.getenv("TAVILY_API_KEY", "")
            tavily_status = "loaded" if tavily_key else "no API key"
        except Exception as e:
            tavily_status = f"error: {str(e)}"
        
        # Get memory status
        memory_status = "not available"
        if conversation_manager:
            memory_status = "redis" if conversation_manager.use_redis else "in-memory"
        
        # Try to create an agent
        agent_ready = False
        try:
            agent = get_agent()
            agent_ready = agent is not None
        except Exception as e:
            logger.error(f"Failed to create agent in health check: {e}")
        
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        api_key_status = "not set"
        if api_key:
            if api_key.startswith("sk-"):
                api_key_status = f"valid format ({api_key[:15]}...)"
            else:
                api_key_status = "invalid format"
        
        return HealthResponse(
            status="healthy",
            tools_count=len(enhanced_mcp_tools),
            agent_ready=agent_ready,
            api_key_status=api_key_status,
            enhanced_mcp_status=enhanced_mcp_status,
            tavily_status=tavily_status,
            memory_status=memory_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            tools_count=0,
            agent_ready=False,
            api_key_status="error",
            enhanced_mcp_status="error",
            tavily_status="error",
            memory_status="error"
        )

@app.post("/api/research")
async def research(request: ResearchRequest):
    """Main research endpoint with conversation memory support."""
    try:
        logger.info(f"Research request received: {request.query[:50]}...")
        logger.info(f"Session ID: {request.sessionId}, Model: {request.model}")
        
        # Use provided session ID or generate new one
        session_id = request.sessionId or generate_session_id()
        
        # Get conversation history if memory is available
        conversation_context = ""
        if conversation_manager and session_id:
            try:
                history = conversation_manager.get_formatted_history(session_id, limit=5)
                if history:
                    conversation_context = f"""
=== Previous Conversation Context ===
{history}
=== End of Context ===

"""
                    logger.info(f"Loaded {len(history.split('\\n'))} lines of conversation history")
            except Exception as e:
                logger.warning(f"Could not load conversation history: {e}")
        
        # Prepare the query with context
        full_query = conversation_context + request.query
        
        # Create a new agent instance
        agent = get_agent(model=request.model)
        if not agent:
            raise HTTPException(status_code=500, detail="Failed to create agent")
        
        logger.info(f"Agent created with {len(agent.tools)} tools for model {request.model}")
        
        # Stream the response
        async def generate():
            start_time = asyncio.get_event_loop().time()
            full_response = ""
            tools_called = []
            thinking_steps = []
            
            try:
                # Process with the agent
                from agents import Runner
                
                # Define message handler
                def message_handler(msg_type, content):
                    nonlocal full_response, tools_called, thinking_steps
                    
                    if msg_type == "content":
                        full_response += content
                        # Stream content
                        data = {"type": "content", "content": content}
                        return f"data: {json.dumps(data)}\n\n"
                    elif msg_type == "thinking":
                        thinking_steps.append(content)
                        # Stream thinking step
                        data = {"type": "thinking", "content": content}
                        return f"data: {json.dumps(data)}\n\n"
                    elif msg_type == "tool":
                        tools_called.append(content)
                        # Stream tool usage
                        data = {"type": "tool", "tool": content}
                        return f"data: {json.dumps(data)}\n\n"
                    return None
                
                # Run the agent with streaming
                response = await Runner.run(
                    starting_agent=agent,
                    input=full_query,
                    context=session_manager.get_session(session_id) if session_id else {},
                    max_turns=5
                )
                
                # Extract content from response
                if hasattr(response, 'messages') and response.messages:
                    for message in response.messages:
                        if hasattr(message, 'content') and message.content:
                            chunk = message.content
                            full_response += chunk
                            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                            
                            # Small delay for smooth streaming
                            await asyncio.sleep(0.01)
                
                # Save to conversation history if available
                if conversation_manager and session_id and full_response:
                    try:
                        conversation_manager.add_entry(
                            session_id=session_id,
                            query=request.query,
                            response=full_response,
                            model=request.model,
                            metadata={
                                "tools_called": tools_called,
                                "thinking_steps": thinking_steps
                            }
                        )
                        logger.info(f"Saved conversation to history for session {session_id}")
                    except Exception as e:
                        logger.warning(f"Could not save conversation history: {e}")
                
                # Send intelligence data if requested
                if request.includeIntelligence:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    intelligence_data = {
                        "type": "intelligence",
                        "content": {
                            "executionTime": int(execution_time * 1000),
                            "tokensUsed": len(full_response.split()) * 2,  # Rough estimate
                            "modelsUsed": [
                                {
                                    "name": request.model,
                                    "purpose": "Primary analysis and response generation",
                                    "tokensUsed": len(full_response.split()) * 2
                                }
                            ],
                            "toolsCalled": tools_called,
                            "thinkingSteps": thinking_steps
                        }
                    }
                    yield f"data: {json.dumps(intelligence_data)}\n\n"
                
                # Session is already saved in conversation_manager above
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error during agent execution: {e}", exc_info=True)
                error_data = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Research endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    if not conversation_manager:
        return {"history": [], "summary": {}}
    
    try:
        history = conversation_manager.get_history(session_id)
        summary = conversation_manager.get_session_summary(session_id)
        
        return {
            "history": [entry.to_dict() for entry in history],
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    if not conversation_manager:
        return {"status": "no memory manager"}
    
    try:
        conversation_manager.clear_session(session_id)
        return {"status": "cleared"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with system information."""
    tools_count = 0
    try:
        mcp_path = os.getenv("MCP_CONFIG_PATH", "./consulting_brain_apis.mcp")
        tools = get_enhanced_mcp_tools(mcp_path)
        tools_count = len(tools)
    except:
        pass
    
    return {
        "service": "Kenton Deep Research API",
        "version": "3.0.0",
        "status": "running",
        "tools_available": tools_count,
        "memory_enabled": conversation_manager is not None,
        "memory_type": "redis" if conversation_manager and conversation_manager.use_redis else "in-memory",
        "endpoints": {
            "health": "/health",
            "research": "/api/research",
            "session_history": "/api/session/{session_id}/history",
            "clear_session": "/api/session/{session_id}"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting API server on {host}:{port}")
    logger.info(f"Memory system: {'Redis' if conversation_manager and conversation_manager.use_redis else 'In-memory'}")
    logger.info(f"To test: curl http://localhost:{port}/health")
    
    uvicorn.run(app, host=host, port=port)