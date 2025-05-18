"""Test script for vector search functionality."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from tools.vector_search import get_file_search_tool
from agents import Runner
from agent_config import get_agent

# Load environment variables
load_dotenv(override=True)

def test_vector_search_configured():
    """Test that FileSearchTool is properly configured."""
    file_search_tool = get_file_search_tool()
    
    if not os.getenv("OPENAI_VECTOR_STORE_ID"):
        print("[Info] OPENAI_VECTOR_STORE_ID not set - FileSearchTool will be None")
        assert file_search_tool is None
    else:
        print("[Success] FileSearchTool configured with vector store ID")
        assert file_search_tool is not None

def test_agent_has_vector_search():
    """Test that the agent includes FileSearchTool when configured."""
    agent = get_agent()
    
    # Check if FileSearchTool is in the agent's tools
    has_file_search = any(
        tool.__class__.__name__ == 'FileSearchTool' 
        for tool in agent.tools
    )
    
    if os.getenv("OPENAI_VECTOR_STORE_ID"):
        assert has_file_search, "FileSearchTool should be present when vector store ID is set"
        print("[Success] Agent includes FileSearchTool")
    else:
        print("[Info] Agent does not include FileSearchTool (no vector store ID)")

if __name__ == "__main__":
    print("Testing vector search configuration...")
    test_vector_search_configured()
    test_agent_has_vector_search()
    print("\nAll tests passed!")