#!/usr/bin/env python3
"""
Test script for MCP API Loader
"""

import unittest
import os
import sys
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp_api_loader import APIManager, create_api_tool, validate_api_config


class TestMCPLoader(unittest.TestCase):
    """Test cases for MCP API Loader."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_mcp_path = "./test_apis.mcp"
        self.sample_config = """
[TestAPI]
name = Test API
endpoint = https://api.test.com/v1/data
auth = TEST_API_KEY
auth_type = Bearer
use_cases = Test API for unit testing
description = A test API configuration

[NoAuthAPI]
name = No Auth API
endpoint = https://api.public.com/v1/data
use_cases = Public API without authentication
description = Public API that doesn't require auth
"""
        
    def test_validate_api_config(self):
        """Test API configuration validation."""
        # Valid config
        valid_config = {
            "name": "Test API",
            "endpoint": "https://api.test.com"
        }
        try:
            validate_api_config("TestAPI", valid_config)
        except KeyError:
            self.fail("Valid config raised KeyError")
        
        # Invalid config (missing endpoint)
        invalid_config = {
            "name": "Test API"
        }
        with self.assertRaises(KeyError):
            validate_api_config("TestAPI", invalid_config)
    
    @patch("requests.get")
    def test_create_api_tool(self, mock_get):
        """Test API tool creation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        # Create tool
        tool = create_api_tool(
            name="TestAPI",
            endpoint="https://api.test.com",
            api_key="test_key",
            auth_type="Bearer",
            description="Test tool"
        )
        
        # Test tool execution
        result = tool(q="test")
        self.assertEqual(result, {"data": "test"})
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[0][0], "https://api.test.com")
        self.assertEqual(call_args[1]["headers"]["Authorization"], "Bearer test_key")
        self.assertEqual(call_args[1]["params"], {"q": "test"})
    
    @patch("requests.get")
    def test_create_api_tool_error_handling(self, mock_get):
        """Test API tool error handling."""
        # Mock failed response
        mock_get.side_effect = Exception("Connection error")
        
        # Create tool
        tool = create_api_tool(
            name="TestAPI",
            endpoint="https://api.test.com",
            api_key="test_key"
        )
        
        # Test tool execution with error
        result = tool()
        self.assertIn("error", result)
        self.assertIn("Connection error", result["error"])
    
    def test_api_manager_load_mcp(self):
        """Test loading MCP configuration."""
        # Create temporary MCP file
        with open(self.test_mcp_path, "w") as f:
            f.write(self.sample_config)
        
        try:
            # Load MCP file
            manager = APIManager(self.test_mcp_path)
            
            # Verify APIs were loaded
            self.assertEqual(len(manager.apis), 2)
            self.assertIn("TestAPI", manager.apis)
            self.assertIn("NoAuthAPI", manager.apis)
            
            # Verify configuration values
            test_api = manager.apis["TestAPI"]
            self.assertEqual(test_api["name"], "Test API")
            self.assertEqual(test_api["endpoint"], "https://api.test.com/v1/data")
            self.assertEqual(test_api["auth"], "TEST_API_KEY")
            
        finally:
            # Clean up
            if os.path.exists(self.test_mcp_path):
                os.remove(self.test_mcp_path)
    
    def test_api_manager_get_tools(self):
        """Test getting tools from API manager."""
        # Create temporary MCP file
        with open(self.test_mcp_path, "w") as f:
            f.write(self.sample_config)
        
        try:
            # Load MCP file
            manager = APIManager(self.test_mcp_path)
            
            # Get tools
            tools = manager.get_tools()
            
            # Verify tools were created
            self.assertEqual(len(tools), 2)
            
            # Verify tool structure
            for tool in tools:
                self.assertIn("name", tool)
                self.assertIn("description", tool)
                self.assertIn("function", tool)
                self.assertTrue(callable(tool["function"]))
            
            # Test get_tool_by_name
            test_tool = manager.get_tool_by_name("TestAPI")
            self.assertIsNotNone(test_tool)
            self.assertEqual(test_tool["name"], "TestAPI")
            
            # Test list_tools
            tool_names = manager.list_tools()
            self.assertIn("TestAPI", tool_names)
            self.assertIn("NoAuthAPI", tool_names)
            
        finally:
            # Clean up
            if os.path.exists(self.test_mcp_path):
                os.remove(self.test_mcp_path)
    
    def test_api_manager_missing_file(self):
        """Test API manager with missing MCP file."""
        # Try to load non-existent file
        manager = APIManager("./nonexistent.mcp")
        
        # Should handle gracefully
        self.assertEqual(len(manager.apis), 0)
        self.assertEqual(len(manager.tools), 0)


if __name__ == "__main__":
    unittest.main()