#!/usr/bin/env python3
"""
Test script to verify the agent uses WeatherAPI for weather queries
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import environment setup
from env_config import setup_environment
setup_environment()

# Import agent configuration 
from agent_config import get_agent
from agents import Runner

async def test_weather_query():
    """Test that the agent correctly uses WeatherAPI for a weather query."""
    logger.info("Initializing agent...")
    agent = get_agent(model="gpt-4.1")
    
    logger.info("\nTesting weather query...")
    query = "What is the current weather in Chicago?"
    result = await Runner.run(agent, query)
    
    # Extract the final output
    if hasattr(result, 'final_output'):
        output = result.final_output
    elif hasattr(result, 'content'):
        output = result.content
    else:
        output = str(result)
    
    logger.info("\nRESULT:")
    logger.info("=" * 80)
    logger.info(output)
    logger.info("=" * 80)
    
    # Check if WeatherAPI was used
    tool_calls = []
    if hasattr(result, 'tool_calls'):
        tool_calls = result.tool_calls
    
    weather_used = any('WeatherAPI' in str(call) for call in tool_calls)
    
    if weather_used:
        logger.info("\n✅ SUCCESS: WeatherAPI was used for the weather query!")
    else:
        logger.error("\n❌ FAILED: WeatherAPI was NOT used for the weather query.")
        logger.error("Tool calls:")
        for call in tool_calls:
            logger.error(f"- {call}")
            
    # Check if any unwanted tools were used
    gdelt_used = any('GDELTAPI' in str(call) for call in tool_calls)
    if gdelt_used:
        logger.error("❌ FAILURE: GDELTAPI was used for weather query!")
    
    return weather_used and not gdelt_used

if __name__ == "__main__":
    success = asyncio.run(test_weather_query())
    sys.exit(0 if success else 1)