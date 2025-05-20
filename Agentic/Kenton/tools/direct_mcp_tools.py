#!/usr/bin/env python3
"""
Direct MCP Tools Module for Kenton project.
Provides simplified wrapper for API tools with better error handling and explicit naming.
"""

import os
import requests
import logging
from typing import List, Dict, Any, Callable
import sys
from pathlib import Path

# Try to import load_dotenv but provide fallback if not available
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback implementation of load_dotenv
    def load_dotenv(dotenv_path=None, stream=None, verbose=False, override=False):
        """Load .env file manually if python-dotenv is not installed."""
        if not dotenv_path:
            dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        if not os.path.exists(dotenv_path):
            return False
            
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                if override or key not in os.environ:
                    os.environ[key] = value
                    
        return True

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import function_tool from agents
try:
    from agents import function_tool
except ImportError:
    # Fallback implementation if agents module is not available
    def function_tool(func):
        return func

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables once
load_dotenv()

def create_api_tool(name: str, endpoint: str, auth_env_var: str = None, 
                   auth_type: str = "Bearer", description: str = None) -> Callable:
    """
    Create a simple API tool function with proper error handling.
    
    Args:
        name: Tool name (will be used as function name)
        endpoint: API endpoint URL
        auth_env_var: Environment variable name for API key
        auth_type: Authentication type (Bearer, API-Key, etc.)
        description: Tool description
        
    Returns:
        Decorated function tool
    """
    
    # Get API key from environment if needed
    api_key = None
    if auth_env_var:
        api_key = os.getenv(auth_env_var)
        if not api_key and auth_env_var != "NONE":
            logger.warning(f"Warning: API key environment variable {auth_env_var} not found for {name}")
    
    @function_tool
    def api_tool(**kwargs):
        """Make an API request with provided parameters."""
        headers = {}
        params = kwargs.copy()
        
        # Handle authentication
        if api_key:
            if auth_type.lower() == "bearer":
                headers["Authorization"] = f"Bearer {api_key}"
            elif auth_type.lower() == "query-key":
                params["key"] = api_key
            elif auth_type.lower() == "api-key":
                headers["X-API-Key"] = api_key
            elif auth_type.lower() == "query-param-apikey":
                params["apikey"] = api_key
            elif auth_type.lower() == "query-param-api_key":
                params["api_key"] = api_key
            elif auth_type.lower() == "x-rapidapi-key":
                headers["X-RapidAPI-Key"] = api_key
                # RapidAPI also needs the host header
                if "rapidapi.com" in endpoint:
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(endpoint)
                    headers["X-RapidAPI-Host"] = parsed_url.netloc
        
        try:
            logger.info(f"[{name}] Making request to {endpoint}")
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except ValueError:
                # If not JSON, return text response
                return {"response": response.text}
                
        except Exception as e:
            logger.error(f"[{name}] Request failed: {e}")
            return {"error": str(e)}
    
    # Update function metadata
    api_tool.__name__ = name
    api_tool.__doc__ = description or f"Make requests to {name}"
    
    return api_tool

def get_mcp_tools() -> List[Callable]:
    """
    Return a list of all API tools with simplified configuration.
    
    Returns:
        List of function tools
    """
    
    tools = []
    
    # WeatherAPI - explicitly defined for maximum clarity
    weather_api = create_api_tool(
        name="WeatherAPI",
        endpoint="https://api.weatherapi.com/v1/current.json",
        auth_env_var="WEATHER_API_KEY",
        auth_type="Query-Key",
        description="Get current weather conditions for any location. ALWAYS use this for weather queries."
    )
    
    # NewsAPI
    news_api = create_api_tool(
        name="NewsAPI",
        endpoint="https://newsapi.org/v2/everything",
        auth_env_var="NEWS_API_KEY",
        auth_type="Bearer",
        description="Fetch latest news articles on various topics. Use for news-related queries."
    )
    
    # MarketDataAPI
    market_api = create_api_tool(
        name="MarketDataAPI",
        endpoint="https://financialmodelingprep.com/api/v3/quote/{symbol}",
        auth_env_var="MARKET_DATA_KEY",
        auth_type="Query-Param-apikey",
        description="Get real-time stock market data and financial indicators."
    )
    
    # FredAPI
    fred_api = create_api_tool(
        name="FredAPI",
        endpoint="https://api.stlouisfed.org/fred/series/observations",
        auth_env_var="FRED_KEY",
        auth_type="Query-Param-api_key",
        description="Access Federal Reserve Economic Data for U.S. macroeconomic indicators."
    )
    
    # GDELTAPI - Include but with clear description
    gdelt_api = create_api_tool(
        name="GDELTAPI",
        endpoint="https://api.gdeltproject.org/api/v2/doc/doc",
        auth_env_var="NONE",
        auth_type="None",
        description="Global news and event monitoring API for trends and events. DO NOT use for weather queries."
    )
    
    # Add tools to list
    tools = [
        weather_api,
        news_api,
        market_api,
        fred_api,
        gdelt_api
    ]
    
    logger.info(f"Loaded {len(tools)} API tools")
    return tools

if __name__ == "__main__":
    # Test functionality when run directly
    tools = get_mcp_tools()
    print(f"Created {len(tools)} tools:")
    for tool in tools:
        print(f"- {tool.__name__}: {tool.__doc__}")