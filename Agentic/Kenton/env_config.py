#!/usr/bin/env python3
"""
Centralized environment configuration module for Kenton project.
Handles .env loading, validation, and cleanup of problematic values.
"""

import os
import sys
from pathlib import Path
import logging

# Try to import load_dotenv but provide fallback if not available
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback implementation of load_dotenv
    def load_dotenv(dotenv_path=None, stream=None, verbose=False, override=False):
        """Load .env file manually if python-dotenv is not installed."""
        if not dotenv_path:
            dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """
    Set up environment variables and verify configuration.
    
    Returns:
        dict: Configuration values from environment variables
    """
    script_dir = Path(__file__).parent.absolute()
    env_file = script_dir / ".env"
    
    # Verify .env file exists
    if not env_file.exists():
        logger.error(f"ERROR: .env file not found at {env_file}")
        sys.exit(1)
    
    # Clear problematic OPENAI variables before loading
    for key in list(os.environ.keys()):
        if key.startswith("OPENAI_"):
            value = os.environ.get(key, "")
            if "…" in value or "\u2026" in value or (key == "OPENAI_API_KEY" and len(value) < 50):
                logger.info(f"Removing problematic {key}")
                del os.environ[key]
    
    # Load environment
    load_dotenv(env_file, override=True)
    
    # Verify API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or len(api_key) < 50:
        logger.error(f"ERROR: Invalid OPENAI_API_KEY (length: {len(api_key)})")
        
        # Try to fix with hardcoded correct key
        correct_key = "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"
        os.environ["OPENAI_API_KEY"] = correct_key
        api_key = correct_key
        logger.info(f"Fixed API key with hardcoded value")
    
    logger.info(f"Environment configured successfully with API key: {api_key[:10]}...")
    
    # Return key configuration values
    return {
        "api_key": api_key,
        "vector_store_id": os.getenv("OPENAI_VECTOR_STORE_ID", ""),
        "weather_api_key": os.getenv("WEATHER_API_KEY", ""),
        "news_api_key": os.getenv("NEWS_API_KEY", ""),
        "market_data_key": os.getenv("MARKET_DATA_KEY", ""),
        "fred_key": os.getenv("FRED_KEY", "")
    }

if __name__ == "__main__":
    # Test configuration when run directly
    config = setup_environment()
    logger.info("Environment configuration test complete")
    for key, value in config.items():
        if key == "api_key":
            # Only show first 10 characters of API key
            logger.info(f"{key}: {value[:10]}... (length: {len(value)})")
        else:
            # Show if value is set or not for other keys
            logger.info(f"{key}: {'SET' if value else 'NOT SET'}")