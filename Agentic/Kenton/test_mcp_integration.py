#!/usr/bin/env python3
"""Test MCP integration with agent configuration."""

from agent_config import get_agent
import os

# Test with different models
models_to_test = ["o3", "gpt-4.1", "gpt-4o"]

for model in models_to_test:
    print(f"\nTesting {model} model...")
    agent = get_agent(model=model)
    print(f"Agent name: {agent.name}")
    print(f"Number of tools: {len(agent.tools)}")
    print(f"Tool types: {[type(tool).__name__ for tool in agent.tools][:5]}...")  # Show first 5