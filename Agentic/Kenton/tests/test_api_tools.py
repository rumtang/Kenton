#!/usr/bin/env python3
"""
Test API tools functionality after MCP removal
Verifies the new API integration approach works correctly
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment first
from dotenv import load_dotenv
load_dotenv(override=True)

# Import components to test
from agent_config import get_agent, get_api_tools
from tools.weather_api import weather_api

class TestAPITools(unittest.TestCase):
    """Test cases for API tools after MCP removal"""
    
    def test_weather_api_error_handling(self):
        """Test weather API error handling with invalid API key"""
        # Mock environment to remove API key
        with patch.dict(os.environ, {"WEATHER_API_KEY": ""}):
            result = weather_api("London")
            self.assertIn("error", result)
            self.assertEqual(result["status"], "error")
            self.assertIn("API key", result["error"].lower())
    
    def test_weather_api_validation(self):
        """Test weather API input validation"""
        result = weather_api("")
        self.assertIn("error", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("location", result["error"].lower())
    
    @patch('tools.weather_api.requests.get')
    def test_weather_api_success(self, mock_get):
        """Test weather API successful response"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "location": {
                "name": "London",
                "region": "",
                "country": "United Kingdom"
            },
            "current": {
                "temp_c": 15.0,
                "temp_f": 59.0,
                "condition": {"text": "Partly cloudy"},
                "wind_kph": 5.6,
                "wind_dir": "SW",
                "humidity": 75,
                "feelslike_c": 14.7,
                "feelslike_f": 58.5
            }
        }
        mock_get.return_value = mock_response
        
        # Test with mock API key
        with patch.dict(os.environ, {"WEATHER_API_KEY": "test_api_key"}):
            result = weather_api("London")
            
            # Verify success
            self.assertNotIn("error", result)
            self.assertEqual(result["status"], "success")
            self.assertIn("display", result)
            self.assertIn("London", result["display"])
    
    def test_get_api_tools(self):
        """Test get_api_tools returns expected tools"""
        # Currently returns empty list as no tools are registered
        tools = get_api_tools()
        self.assertIsInstance(tools, list)
    
    def test_agent_config(self):
        """Test agent configuration doesn't try to load MCP tools"""
        agent = get_agent()
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.tools)
        
        # Check for presence of required tools
        tool_names = [getattr(tool, '__name__', str(tool)) for tool in agent.tools]
        self.assertIn('summarize', tool_names)
        self.assertIn('compare_sources', tool_names)
        self.assertIn('generate_report', tool_names)
        self.assertIn('file_search', tool_names)
        
        # MCP tools should not be present
        self.assertNotIn('weather_api_mcp', tool_names)
        self.assertNotIn('news_api_mcp', tool_names)
        self.assertNotIn('get_mcp_tools', tool_names)

if __name__ == '__main__':
    unittest.main()