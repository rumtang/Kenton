#!/usr/bin/env python3
"""
MCP API Loader Module
Loads an INI-style .mcp file that lists APIs and their configurations,
creates callable tools for each API, and returns them in a format suitable
for OpenAI SDK agent builders.
"""

from configparser import ConfigParser
from dotenv import load_dotenv
import os
import requests
import logging
from typing import Dict, List, Any, Callable
from functools import partial

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_api_config(name: str, config: Dict[str, str]) -> None:
    """Validate that required keys are present in API configuration."""
    required_keys = ['endpoint', 'name']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise KeyError(f"API '{name}' missing required keys: {missing_keys}")


def create_api_tool(name: str, endpoint: str, api_key: str = None, 
                   auth_type: str = "Bearer", description: str = None) -> Callable:
    """
    Create a callable tool function for an API endpoint.
    
    Args:
        name: API name
        endpoint: API endpoint URL
        api_key: API key for authentication
        auth_type: Authentication type (Bearer, API-Key, Query-Key, etc.)
        description: Tool description
    
    Returns:
        Callable function that makes API requests
    """
    def api_tool_function(**kwargs) -> Dict[str, Any]:
        """Make API request with provided parameters."""
        headers = {}
        query_params = kwargs.copy()
        
        # Handle authentication based on type
        if api_key:
            if auth_type.lower() == "bearer":
                headers["Authorization"] = f"Bearer {api_key}"
            elif auth_type.lower() == "api-key":
                headers["X-API-Key"] = api_key
            elif auth_type.lower() == "query-key":
                # For APIs that expect key as query parameter (like weatherapi.com)
                query_params["key"] = api_key
            elif auth_type.lower() == "query-param-apikey":
                # For APIs expecting 'apikey' parameter (like FMP)
                query_params["apikey"] = api_key
            elif auth_type.lower() == "query-param-api_key":
                # For APIs expecting 'api_key' parameter (like FRED)
                query_params["api_key"] = api_key
            elif auth_type.lower() == "x-rapidapi-key":
                headers["X-RapidAPI-Key"] = api_key
                # RapidAPI also needs the host header
                if "rapidapi.com" in endpoint:
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(endpoint)
                    headers["X-RapidAPI-Host"] = parsed_url.netloc
            else:
                headers["Authorization"] = f"{auth_type} {api_key}"
        
        try:
            logger.info(f"[{name}] Making request to {endpoint}")
            response = requests.get(endpoint, headers=headers, params=query_params, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except ValueError:
                # If not JSON, return text response
                return {"response": response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[{name}] Request failed: {e}")
            return {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"[{name}] Unexpected error: {e}")
            return {"error": str(e), "status": "error"}
    
    # Set function metadata for OpenAI tools
    api_tool_function.__name__ = name.replace(" ", "_").lower()
    api_tool_function.__doc__ = description or f"API tool for {name}"
    
    return api_tool_function


class APIManager:
    """Manages API tools loaded from MCP configuration file."""
    
    def __init__(self, mcp_path: str = "./consulting_brain_apis.mcp"):
        """
        Initialize API Manager with MCP file.
        
        Args:
            mcp_path: Path to MCP configuration file
        """
        self.mcp_path = mcp_path
        self.apis = self._load_mcp(mcp_path)
        self.tools = self._build_tools()
        logger.info(f"Loaded {len(self.tools)} API tools from {mcp_path}")
    
    def _load_mcp(self, filepath: str) -> Dict[str, Dict[str, str]]:
        """
        Load and parse MCP configuration file.
        
        Args:
            filepath: Path to MCP file
            
        Returns:
            Dictionary of API configurations
        """
        if not os.path.exists(filepath):
            logger.warning(f"MCP file not found: {filepath}")
            return {}
            
        config = ConfigParser()
        config.read(filepath)
        
        apis = {}
        for section in config.sections():
            apis[section] = dict(config.items(section))
            logger.debug(f"Loaded API config: {section}")
            
        return apis
    
    def _build_tools(self) -> List[Dict[str, Any]]:
        """
        Build tool functions from API configurations.
        
        Returns:
            List of tool dictionaries with name, description, and function
        """
        tools = []
        
        for api_name, config in self.apis.items():
            try:
                # Validate required configuration
                validate_api_config(api_name, config)
                
                # Extract configuration values
                endpoint = config.get("endpoint", "").strip()
                auth_key_env = config.get("auth", "").strip()
                auth_type = config.get("auth_type", "Bearer").strip()
                use_case = config.get("use_cases", f"API tool for {api_name}")
                description = config.get("description", use_case)
                
                # Get API key from environment if specified
                api_key = None
                if auth_key_env:
                    api_key = os.getenv(auth_key_env)
                    if not api_key:
                        logger.warning(f"[{api_name}] API key '{auth_key_env}' not found in environment")
                
                # Create the tool function
                tool_function = create_api_tool(
                    name=api_name,
                    endpoint=endpoint,
                    api_key=api_key,
                    auth_type=auth_type,
                    description=description
                )
                
                # Create tool dictionary for OpenAI SDK
                tool_dict = {
                    "name": api_name,
                    "description": description,
                    "function": tool_function,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
                
                tools.append(tool_dict)
                logger.info(f"Created tool: {api_name}")
                
            except Exception as e:
                logger.warning(f"Skipping {api_name} due to error: {e}")
                
        return tools
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of API tools.
        
        Returns:
            List of tool dictionaries
        """
        return self.tools
    
    def get_tool_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get a specific tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool dictionary or None if not found
        """
        for tool in self.tools:
            if tool["name"] == name:
                return tool
        return None
    
    def list_tools(self) -> List[str]:
        """
        Get list of tool names.
        
        Returns:
            List of tool names
        """
        return [tool["name"] for tool in self.tools]


# Example MCP file content:
"""
[NewsAPI]
name = News API
endpoint = https://newsapi.org/v2/everything
auth = NEWS_API_KEY
auth_type = Bearer
use_cases = Fetch latest news articles on various topics
description = News API for retrieving articles from various sources

[WeatherAPI]
name = Weather API
endpoint = https://api.weatherapi.com/v1/current.json
auth = WEATHER_API_KEY
auth_type = api-key
use_cases = Get current weather conditions for any location
description = Weather API for current conditions

[CompanyInfo]
name = Company Information API  
endpoint = https://api.company-info.com/v1/companies
auth = COMPANY_API_KEY
auth_type = Bearer
use_cases = Retrieve detailed company information and profiles
description = API for company data and profiles
"""


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize API manager
        manager = APIManager("./consulting_brain_apis.mcp")
        
        # Get all tools
        tools = manager.get_tools()
        
        print(f"\nLoaded {len(tools)} tools:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
        
        # Example: Use a tool
        if tools:
            first_tool = tools[0]
            print(f"\nTesting {first_tool['name']}...")
            result = first_tool['function'](q="openai", limit=5)
            print(f"Result: {result}")
            
    except Exception as e:
        logger.error(f"Error in example: {e}")