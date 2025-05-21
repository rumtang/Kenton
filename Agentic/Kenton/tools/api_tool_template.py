#!/usr/bin/env python3
"""
API Tool Template for integrating external APIs
This template provides structure for adding new API integrations with error handling,
validation patterns, and compatibility with OpenAI Agents SDK.
"""

import os
import logging
import requests
import json
import time
from functools import wraps
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import agents SDK, but provide fallback if not available
try:
    from agents import function_tool
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI Agents SDK not available, using fallback implementation")
    AGENTS_SDK_AVAILABLE = False
    
    # Simple fallback implementation
    def function_tool(func):
        """Simple fallback implementation of function_tool decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

# Import error handling utilities
try:
    from tools.errors import AgentExecutionError, create_api_key_error, create_network_error
except ImportError:
    # Fallback error classes if errors.py is not available
    class AgentExecutionError(Exception):
        """Base exception class for API-related errors."""
        def __init__(self, message, code=None, hint=None, resolution=None, details=None):
            self.message = message
            self.code = code or "API-ERR-000"
            self.hint = hint
            self.resolution = resolution
            self.details = details or {}
            super().__init__(message)
            
        def __str__(self):
            lines = [f"ERROR-{self.code}: {self.message}"]
            if self.hint:
                lines.append(f"- Problem: {self.hint}")
            if self.resolution:
                lines.append(f"- Solution: {self.resolution}")
            return "\n".join(lines)
    
    def create_api_key_error(service_name, details=None):
        return AgentExecutionError(
            message=f"{service_name.upper()} API key error",
            code="AUTH001",
            hint=f"Missing or invalid {service_name} API key",
            resolution=f"Check your .env file for a valid {service_name.upper()}_API_KEY",
            details=details
        )
    
    def create_network_error(service_name, original_error):
        return AgentExecutionError(
            message=f"Network error connecting to {service_name}: {str(original_error)}",
            code="NET001",
            hint="Network connectivity issue or service unavailability",
            resolution="Check your internet connection and service status",
            details={"original_error": str(original_error)}
        )

# Constants
DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_RETRIES = 2
DEFAULT_RETRY_DELAY = 1  # seconds

def with_retry(max_retries: int = DEFAULT_RETRIES, retry_delay: int = DEFAULT_RETRY_DELAY):
    """
    Decorator that adds retry logic to API functions.
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries (with exponential backoff)
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_error = None
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.Timeout as e:
                    retries += 1
                    last_error = e
                    delay = retry_delay * (2 ** retries)  # Exponential backoff
                    logger.warning(f"Timeout error in {func.__name__}, retrying {retries}/{max_retries} in {delay}s")
                    time.sleep(delay)
                except requests.exceptions.ConnectionError as e:
                    retries += 1
                    last_error = e
                    delay = retry_delay * (2 ** retries)  # Exponential backoff
                    logger.warning(f"Connection error in {func.__name__}, retrying {retries}/{max_retries} in {delay}s")
                    time.sleep(delay)
                except requests.exceptions.RequestException as e:
                    # Don't retry other request exceptions (400 errors, etc.)
                    status_code = None
                    response_text = None
                    
                    if hasattr(e, 'response') and e.response:
                        status_code = e.response.status_code
                        try:
                            response_text = e.response.json()
                        except:
                            response_text = e.response.text
                    
                    error_message = f"API request failed: {str(e)}"
                    logger.error(f"{error_message} - Status: {status_code}")
                    return {
                        "error": error_message,
                        "status": "error",
                        "status_code": status_code,
                        "response": response_text
                    }
            
            # If we've exhausted all retries
            if last_error:
                logger.error(f"All retries failed for {func.__name__}: {str(last_error)}")
                return {
                    "error": f"Failed after {max_retries} retries: {str(last_error)}",
                    "status": "error",
                    "details": "Request timed out repeatedly"
                }
            
            return func(*args, **kwargs)  # This should never be reached
        return wrapper
    return decorator

def validate_api_key(api_key: str, api_name: str) -> None:
    """
    Validate that an API key exists and is not empty.
    
    Args:
        api_key: The API key to validate
        api_name: The name of the API (for error reporting)
        
    Raises:
        AgentExecutionError: If the API key is missing or invalid
    """
    if not api_key:
        raise create_api_key_error(api_name)
    
    # Check for common issues with API keys
    if len(api_key) < 10:  # Most APIs have longer keys
        raise create_api_key_error(
            api_name, 
            details={"hint": "API key appears to be too short"}
        )

def format_response(data: Union[Dict[str, Any], List, str], include_raw: bool = False) -> Dict[str, Any]:
    """
    Format API response consistently.
    
    Args:
        data: The API response data
        include_raw: Whether to include the raw data in the response
        
    Returns:
        Formatted response dictionary
    """
    # Handle error responses
    if isinstance(data, dict) and "error" in data:
        return data
    
    # Prepare successful response
    response = {
        "status": "success",
    }
    
    # Include the raw data if requested
    if include_raw:
        response["raw_data"] = data
    
    # For dictionary responses
    if isinstance(data, dict):
        # Extract relevant fields based on the response structure
        # This should be customized for each API
        response["data"] = data
        
        # Add a display field for better human readability if not present
        if "display" not in data:
            # Create a simple display representation
            if len(data) > 0:
                display_lines = [f"{k}: {v}" for k, v in data.items() if k != "raw_data"]
                response["display"] = "\n".join(display_lines)
            else:
                response["display"] = "No data returned"
    
    # For list responses
    elif isinstance(data, list):
        response["data"] = data
        
        # Create a summary for display
        if len(data) > 0:
            response["display"] = f"Retrieved {len(data)} items"
        else:
            response["display"] = "No items returned"
    
    # For string responses
    else:
        response["data"] = data
        response["display"] = str(data)
    
    return response

# Example API tool implementation
@function_tool
@with_retry(max_retries=2)
def example_api(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Example API tool implementation.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        Formatted API response
    """
    # Get API key from environment
    api_key = os.environ.get("EXAMPLE_API_KEY", "")
    
    # Validate API key
    try:
        validate_api_key(api_key, "example")
    except AgentExecutionError as e:
        return {"error": str(e), "status": "error"}
    
    # Set up request parameters
    url = "https://api.example.com/v1/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"q": query, "limit": limit}
    
    try:
        # Make the request
        logger.info(f"Making API request to {url} with query: {query}")
        response = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response",
                "status": "error",
                "response": response.text
            }
        
        # Format and return the response
        return format_response(data)
        
    except requests.exceptions.Timeout:
        # Let the retry decorator handle this
        raise
    except requests.exceptions.ConnectionError:
        # Let the retry decorator handle this
        raise
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx, 5xx)
        status_code = e.response.status_code
        try:
            error_data = e.response.json()
            error_message = error_data.get("message", str(e))
        except:
            error_message = e.response.text or str(e)
        
        return {
            "error": f"HTTP error: {error_message}",
            "status": "error",
            "status_code": status_code
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in example_api: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }

# This template can be used as a starting point for implementing new API tools
# Replace the example_api function with your own API implementation
# Use the provided utility functions for consistent error handling and formatting