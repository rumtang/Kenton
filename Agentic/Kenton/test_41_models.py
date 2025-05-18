#!/usr/bin/env python3
"""Test script to check 4.1 model family availability."""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def test_41_models():
    """Test 4.1 model family variants."""
    client = OpenAI()
    
    print("Testing 4.1 model family variants...\n")
    
    models_to_test = [
        "4.1",
        "gpt-4.1",
        "gpt-4.1-preview",
        "gpt-4.1-turbo",
        "4.1-mini",
        "gpt-4.1-mini"
    ]
    
    successful_models = []
    
    for model in models_to_test:
        print(f"Testing model: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Say 'yes' in one word."}
                ],
                max_completion_tokens=100
            )
            print(f"✅ SUCCESS: {model} is accessible!")
            print(f"Response: {response.choices[0].message.content}")
            print(f"Model used: {response.model}\n")
            successful_models.append(model)
            
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "model_not_found" in error_msg:
                print(f"❌ FAILED: {model} - Model not found")
            elif "verified" in error_msg:
                print(f"❌ FAILED: {model} - Organization verification required")
            elif "parameter" in error_msg:
                print(f"❌ FAILED: {model} - Parameter issue: {error_msg[:100]}...")
            else:
                print(f"❌ FAILED: {model} - {error_msg[:100]}...")
            print()
    
    print("\n=== SUMMARY ===")
    print(f"Accessible 4.1 models: {', '.join(successful_models) if successful_models else 'None'}")
    
    return successful_models

if __name__ == "__main__":
    accessible_models = test_41_models()