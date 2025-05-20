#!/usr/bin/env python3
"""
Fix environment variables permanently by creating a correct .env file.
This addresses the issue of corrupted OPENAI_API_KEY (containing ellipsis).
"""

import os
import sys
from pathlib import Path
import subprocess

def create_fresh_env_file():
    """Create a fresh .env file with the correct API key."""
    env_path = Path('./.env')
    
    # Correct API key - this is the actual working key for this project
    api_key = "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"
    
    # Backup existing .env if it exists
    if env_path.exists():
        backup_path = env_path.with_suffix('.env.bak')
        try:
            with open(env_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"✅ Backed up existing .env to {backup_path}")
        except Exception as e:
            print(f"⚠️ Failed to backup .env: {e}")
    
    # Create a fresh .env file
    try:
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write("OPENAI_BASE_URL=https://api.openai.com/v1\n")
            # Add any other required environment variables
            # f.write("VECTOR_STORE_ID=your_vector_store_id\n")
        print(f"✅ Created fresh .env file with correct API key")
        
        # Set proper permissions to ensure it's secure
        try:
            subprocess.run(['chmod', '600', str(env_path)], check=True)
            print(f"✅ Set secure permissions on .env file")
        except Exception as e:
            print(f"⚠️ Failed to set permissions: {e}")
            
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_env_file():
    """Test the .env file by loading it with a new process."""
    try:
        result = subprocess.run(
            ['python', '-c', 'import os; from dotenv import load_dotenv; load_dotenv(); print(f"API KEY: {os.environ.get(\"OPENAI_API_KEY\", \"NOT SET\")[:10]}...")'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Test successful: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Permanently fixing environment variables...")
    
    if create_fresh_env_file():
        test_env_file()
        print("\n🎉 Fix complete! Please restart all services for changes to take effect.")
        print("Run: ./stop_all.sh && ./start_all.sh")
    else:
        print("\n❌ Failed to fix environment variables.")