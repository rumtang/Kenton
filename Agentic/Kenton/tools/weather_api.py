#!/usr/bin/env python3
"""
Weather API Tool
Simple example of an API integration using OpenAI Agents SDK without MCP dependencies.
"""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional

# Import the utility functions from the template
from tools.api_tool_template import (
    with_retry, validate_api_key, format_response, 
    DEFAULT_TIMEOUT, AgentExecutionError, create_api_key_error
)

# Try to import agents SDK, but provide fallback if not available
try:
    from agents import function_tool
except ImportError:
    from tools.api_tool_template import function_tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@function_tool
@with_retry(max_retries=2)
def weather_api(location: str) -> Dict[str, Any]:
    """
    Get current weather conditions for any location.
    
    Args:
        location: The location to get weather for (city name, zip code, coordinates)
        
    Returns:
        Formatted weather data response
    """
    # Get API key from environment
    api_key = os.environ.get("WEATHER_API_KEY", "")
    
    # Validate API key
    try:
        validate_api_key(api_key, "weather")
    except AgentExecutionError as e:
        return {"error": str(e), "status": "error"}
    
    # Validate input
    if not location or len(location.strip()) == 0:
        return {
            "error": "Location parameter cannot be empty",
            "status": "error",
            "hint": "Please provide a valid location like 'New York', 'London', etc."
        }
    
    # Set up request
    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": location}
    
    try:
        # Make the request
        logger.info(f"Making weather API request for location: {location}")
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        
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
        
        # Check for required fields
        if "location" not in data or "current" not in data:
            return {
                "error": "Invalid response format",
                "status": "error",
                "hint": "API response is missing required fields"
            }
        
        # Add formatted display
        location_info = data['location']
        current = data['current']
        
        data["display"] = f"""Weather for {location_info['name']}, {location_info.get('region', '')}, {location_info['country']}:
- Temperature: {current['temp_c']}°C / {current['temp_f']}°F
- Conditions: {current['condition']['text']}
- Wind: {current['wind_kph']} kph ({current['wind_dir']})
- Humidity: {current['humidity']}%
- Feels like: {current['feelslike_c']}°C / {current['feelslike_f']}°F"""
        
        # Return formatted response
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
            if "error" in error_data:
                error_message = error_data["error"].get("message", str(e))
            else:
                error_message = str(e)
        except:
            error_message = e.response.text or str(e)
        
        return {
            "error": f"Weather API error: {error_message}",
            "status": "error",
            "status_code": status_code
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in weather_api: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }

# Verify the tool is properly registered
if __name__ == "__main__":
    # Test the weather API tool
    print("Testing weather API tool...")
    
    if "WEATHER_API_KEY" not in os.environ:
        print("Warning: WEATHER_API_KEY not found in environment")
        print("Please set WEATHER_API_KEY in your .env file")
    else:
        # Test with a valid location
        result = weather_api(location="London")
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("Success!")
            print(result.get("display", "No display available"))