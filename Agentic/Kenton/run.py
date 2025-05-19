#!/usr/bin/env python3
"""Launch script that uses .env file for configuration"""

import os
import sys
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()
env_file = script_dir / ".env"

# Make sure we're using the local .env file
if not env_file.exists():
    print(f"ERROR: .env file not found at {env_file}")
    sys.exit(1)

# Clear any problematic OPENAI variables to ensure we use .env
for key in list(os.environ.keys()):
    if key.startswith("OPENAI_"):
        # Remove if it contains problematic characters or is too short
        value = os.environ.get(key, "")
        if "…" in value or "\u2026" in value or (key == "OPENAI_API_KEY" and len(value) < 50):
            print(f"Removing problematic {key}: {value[:20]}...")
            del os.environ[key]

# Load environment from .env file
from dotenv import load_dotenv
load_dotenv(env_file, override=True)

# Verify we have a valid API key
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key or len(api_key) < 50:
    print(f"ERROR: Invalid OPENAI_API_KEY loaded (length: {len(api_key)})")
    if api_key:
        print(f"Key starts with: {api_key[:20]}")
    print("Please check your .env file")
    sys.exit(1)

# Double-check for ellipsis
if "…" in api_key or "\u2026" in api_key:
    print("ERROR: API key contains ellipsis character - environment is corrupted")
    print("Please restart your terminal and try again")
    sys.exit(1)

print(f"Using API key from .env: {api_key[:15]}... (verified length: {len(api_key)})")

# Run the main application
from main import main
main()