#!/usr/bin/env python3
"""
Example of using MCP API tools with OpenAI SDK agents
"""

import os
import sys

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp_api_loader import APIManager
from agents import Agent, Runner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_research_agent_with_mcp_tools():
    """Create a research agent with MCP-loaded API tools."""
    
    # Load API tools from MCP file
    api_manager = APIManager("./consulting_brain_apis.mcp")
    mcp_tools = api_manager.get_tools()
    
    # Convert MCP tools to OpenAI SDK format
    openai_tools = []
    for tool in mcp_tools:
        # Each tool needs to be a callable function for OpenAI SDK
        openai_tools.append(tool["function"])
    
    # Create agent with loaded tools
    agent = Agent(
        name="ConsultingResearcher",
        instructions="""
        You are a consulting researcher with access to various APIs.
        Use the available tools to gather information about:
        - Current news and events
        - Company information
        - Market data
        - Industry reports
        - Weather conditions
        
        Always cite your sources and provide comprehensive analysis.
        """,
        model="gpt-4o",
        tools=openai_tools
    )
    
    return agent


def main():
    """Example usage of MCP tools with agents."""
    
    # Create agent with MCP tools
    print("Creating research agent with MCP-loaded tools...")
    agent = create_research_agent_with_mcp_tools()
    
    # Example queries
    queries = [
        "What's the latest news about artificial intelligence in finance?",
        "Get me information about Apple Inc. and current market conditions",
        "What's the weather like in New York City right now?",
    ]
    
    # Run queries
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            result = Runner.run_sync(agent, query)
            print(f"Response: {result.final_output[:500]}...")  # Truncate for display
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()