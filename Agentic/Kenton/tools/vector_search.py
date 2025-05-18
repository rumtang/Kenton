# Tool: Vector Search - Uses OpenAI's native vector store capability

from agents import function_tool
from agents import FileSearchTool
import os

# Note: This is a wrapper around the native FileSearchTool for easier configuration
# The actual FileSearchTool is added directly to the agent in agent_config.py

@function_tool
def vector_search(query: str) -> str:
    """Search through vectorized documents using OpenAI's file search capability."""
    
    # Get vector store ID from environment
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID", "")
    
    if not vector_store_id:
        return "[Vector Search Error] OPENAI_VECTOR_STORE_ID not found in environment. Please set it in your .env file."
    
    # Note: In actual usage, the FileSearchTool is instantiated in agent_config.py
    # This function is here for documentation and testing purposes
    return f"[Vector Search] This is a placeholder. The actual FileSearchTool is configured in agent_config.py with vector_store_id: {vector_store_id}"

# Export the actual tool configuration
def get_file_search_tool():
    """Get configured FileSearchTool instance for the agent."""
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID", "")
    
    if not vector_store_id:
        print("[Warning] OPENAI_VECTOR_STORE_ID not set, FileSearchTool will not work")
        return None
    
    return FileSearchTool(
        vector_store_ids=[vector_store_id],
        max_num_results=5,
        include_search_results=True
    )