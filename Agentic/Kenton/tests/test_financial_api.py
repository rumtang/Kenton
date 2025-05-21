#!/usr/bin/env python3
"""
Test script for Financial Modeling Prep API integration.
"""

import os
import sys
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the financial API tools
try:
    from tools.financial_api import (
        company_profile, stock_price, test_financial_api_connection
    )
except ImportError:
    print("Error: Financial API tools not found.")
    sys.exit(1)

def main():
    """Test the Financial Modeling Prep API integration."""
    print("=== Financial Modeling Prep API Integration Test ===\n")
    
    # Check environment
    api_key = os.environ.get("MARKET_DATA_KEY")
    if not api_key:
        print("ERROR: MARKET_DATA_KEY not set in environment")
        print("Please add your Financial Modeling Prep API key to .env file")
        return
    
    # Show masked API key for verification
    masked_key = api_key[:5] + '*' * (len(api_key) - 10) + api_key[-5:] if len(api_key) > 10 else "*****"
    print(f"API Key: {masked_key}")
    
    # Test API connection
    print("\n== Testing API Connection ==")
    test_result = test_financial_api_connection()
    print(f"Status: {test_result['status']}")
    print(f"Message: {test_result['message']}")
    
    if test_result['status'] != 'success':
        print("API connection test failed. Please check your API key and internet connection.")
        return
    
    # Test specific endpoints
    print("\n== Testing Company Profile API ==")
    try:
        result = company_profile("AAPL")
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("SUCCESS: Company profile retrieved")
            if "display" in result:
                print("\nSample data:")
                print(result["display"])
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n== Testing Stock Price API ==")
    try:
        result = stock_price("MSFT")
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("SUCCESS: Stock price retrieved")
            if "display" in result:
                print("\nSample data:")
                print(result["display"])
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()