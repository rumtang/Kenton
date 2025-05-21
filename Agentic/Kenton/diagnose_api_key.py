#!/usr/bin/env python3
"""
API Key Diagnostic Tool
Helps diagnose API key issues by checking formats and testing API connectivity
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_masked_key(key, prefix=4, suffix=4):
    """Print a masked version of an API key for security."""
    if not key:
        return "None"
    if len(key) <= prefix + suffix:
        return "*" * len(key)
    return f"{key[:prefix]}{'*' * (len(key) - prefix - suffix)}{key[-suffix:]}"

def check_key_format(key):
    """Check if the API key format is valid."""
    if not key:
        return {
            "valid": False,
            "reason": "API key is missing"
        }
    
    # Check for ellipsis characters
    if '…' in key or '\u2026' in key:
        return {
            "valid": False,
            "reason": "API key contains ellipsis characters"
        }
    
    # Check for standard API key format
    if key.startswith("sk-") and not key.startswith("sk-proj-") and len(key) >= 40:
        return {
            "valid": True,
            "key_type": "standard",
            "format": "Valid standard API key"
        }
    
    # Check for project-scoped API key format
    if key.startswith("sk-proj-") and len(key) >= 60:
        return {
            "valid": True,
            "key_type": "project-scoped",
            "format": "Valid project-scoped API key"
        }
    
    # Key doesn't match any expected format
    return {
        "valid": False,
        "reason": f"Invalid API key format: {key[:10]}... (length: {len(key)})"
    }

def test_api_connectivity(key):
    """Test API connectivity with the given key."""
    if not key:
        return {
            "success": False,
            "message": "No API key provided"
        }
    
    # Test the models endpoint
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json().get("data", [])
            model_count = len(models)
            return {
                "success": True,
                "message": f"Successfully connected to API. Found {model_count} models.",
                "status_code": response.status_code
            }
        else:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_message = error_data["error"].get("message", "Unknown error")
            except:
                error_message = response.text
            
            return {
                "success": False,
                "message": f"API connection failed: {error_message}",
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}"
        }

def main():
    """Run the API key diagnostic tool."""
    print("=== OpenAI API Key Diagnostic Tool ===\n")
    
    # Check if API key is in environment
    api_key = os.getenv("OPENAI_API_KEY", "")
    print(f"API Key in environment: {'Yes' if api_key else 'No'}")
    
    if api_key:
        print(f"API Key preview: {print_masked_key(api_key)}")
        print(f"API Key length: {len(api_key)} characters")
        
        # Check API key format
        format_check = check_key_format(api_key)
        if format_check["valid"]:
            print(f"API Key format: ✅ {format_check['format']}")
            print(f"API Key type: {format_check['key_type']}")
            
            # Test API connectivity
            print("\nTesting API connectivity...")
            connectivity = test_api_connectivity(api_key)
            
            if connectivity["success"]:
                print(f"✅ API connection successful: {connectivity['message']}")
            else:
                print(f"❌ API connection failed: {connectivity['message']}")
                
                # If it's a project-scoped key, add additional info
                if format_check["key_type"] == "project-scoped":
                    print("\n⚠️ IMPORTANT: You're using a project-scoped API key")
                    print("Project-scoped keys may be restricted to specific operations.")
                    print("If you're getting API authentication errors, try:")
                    print("1. Updating to OpenAI SDK v1.79.0 or newer")
                    print("2. Confirming this key has access to the APIs you're using")
                    print("3. Using a standard API key instead (starting with 'sk-')")
        else:
            print(f"❌ API Key format: Invalid - {format_check['reason']}")
    else:
        print("❌ No API key found in environment")
        print("1. Create a .env file in the project root")
        print("2. Add the line: OPENAI_API_KEY=your_api_key_here")
        print("3. Restart your application")
    
    print("\n=== Diagnostic Complete ===")

if __name__ == "__main__":
    main()