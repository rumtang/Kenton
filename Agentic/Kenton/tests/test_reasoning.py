#!/usr/bin/env python3
"""
Test script for OpenAI reasoning capabilities in Kenton Deep Research Agent.
Tests both the agent configuration and API server integration.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required project modules
from dotenv import load_dotenv
from agent_config import get_agent
from agents import Runner

# Load environment variables for testing
load_dotenv()

class TestReasoningCapabilities(unittest.TestCase):
    """Test reasoning capabilities in Kenton Deep Research Agent"""
    
    def test_agent_config_with_reasoning(self):
        """Test that agent_config.py correctly sets up reasoning parameter"""
        # Test with reasoning disabled (default)
        agent = get_agent(model="o3")
        self.assertFalse(
            getattr(agent.model_settings, 'enable_reasoning', False),
            "enable_reasoning should be False by default"
        )
        
        # Test with reasoning enabled
        agent_with_reasoning = get_agent(model="o3", enable_reasoning=True)
        self.assertTrue(
            getattr(agent_with_reasoning.model_settings, 'enable_reasoning', False),
            "enable_reasoning should be True when explicitly enabled"
        )
        
        # Test with incompatible model
        agent_incompatible = get_agent(model="gpt-3.5-turbo", enable_reasoning=True)
        self.assertFalse(
            getattr(agent_incompatible.model_settings, 'enable_reasoning', False),
            "enable_reasoning should not be set for incompatible models"
        )
    
    @patch('agents.Runner.run')
    async def test_reasoning_in_api_response(self, mock_run):
        """Test that reasoning trace is correctly extracted from response"""
        # Mock the agent result with reasoning trace
        mock_result = MagicMock()
        mock_result.final_output = "This is the final research output"
        mock_result.reasoning_trace = "This is the reasoning process"
        mock_run.return_value = mock_result
        
        # Import the API module
        from fixed_api_server import app
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Test request with reasoning enabled
        response = client.post(
            "/api/research",
            json={"query": "Test query", "model": "o3", "enable_reasoning": True}
        )
        
        # Check if the reasoning_trace was correctly processed
        found_reasoning_start = False
        found_reasoning_data = False
        found_reasoning_end = False
        
        # Parse the SSE events
        events = response.content.decode().strip().split('\n\n')
        for event in events:
            if event.startswith('data: '):
                data = json.loads(event[6:])
                if data.get('type') == 'reasoning_start':
                    found_reasoning_start = True
                elif data.get('type') == 'reasoning':
                    found_reasoning_data = True
                elif data.get('type') == 'reasoning_end':
                    found_reasoning_end = True
                elif data.get('type') == 'complete':
                    self.assertTrue(data.get('reasoning_available', False),
                                   "completion should indicate reasoning is available")
        
        self.assertTrue(found_reasoning_start, "Should include reasoning_start event")
        self.assertTrue(found_reasoning_data, "Should include reasoning data events")
        self.assertTrue(found_reasoning_end, "Should include reasoning_end event")
    
    def test_cli_reasoning_parameter(self):
        """Test that the CLI properly handles the reasoning parameter"""
        from main import run_agent
        
        # Mock Runner.run_sync to avoid actual API calls
        with patch('agents.Runner.run_sync') as mock_run_sync:
            # Mock the agent result
            mock_result = MagicMock()
            mock_result.final_output = "Test output"
            mock_result.reasoning_trace = "Test reasoning"
            mock_run_sync.return_value = mock_result
            
            # Test with reasoning disabled
            run_agent("Test query", "o3", enable_reasoning=False)
            
            # Check that the agent was created with the right parameters
            agent = mock_run_sync.call_args[0][0]
            self.assertFalse(
                getattr(agent.model_settings, 'enable_reasoning', False),
                "Agent should be created with reasoning disabled"
            )
            
            # Reset mock
            mock_run_sync.reset_mock()
            
            # Test with reasoning enabled
            run_agent("Test query", "o3", enable_reasoning=True)
            
            # Check that the agent was created with the right parameters
            agent = mock_run_sync.call_args[0][0]
            self.assertTrue(
                getattr(agent.model_settings, 'enable_reasoning', True),
                "Agent should be created with reasoning enabled"
            )

if __name__ == "__main__":
    unittest.main()