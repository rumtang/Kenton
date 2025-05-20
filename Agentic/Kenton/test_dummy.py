#!/usr/bin/env python3
"""
Dummy script to test the frontend response handling
"""

import sys
import time
import argparse

def main():
    """Simulate a report for testing purposes"""
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument('--model', default='o3', help='Model name')
    parser.add_argument('--query', help='Research query')
    args = parser.parse_args()
    
    # Output like the real script does
    print(f"Initializing Deep Research Agent with {args.model}...")
    time.sleep(1)
    print(f"Loaded 5 MCP tools for OpenAI")
    time.sleep(1)
    
    # Start the research
    print(f"\n🔬 Starting research on: {args.query}\n")
    time.sleep(2)
    
    # Output the report header
    print("\n📊 Final Research Report:\n")
    print("==================================================")
    time.sleep(1)
    
    # Output some multiline content 
    report = """Here is a detailed report on your query:

1. Introduction
   This is an introduction to the topic.
   It contains multiple paragraphs.

2. Analysis
   Here is some analysis of the situation.
   With supporting details.
   And more information.

3. Recommendations
   - First recommendation
   - Second recommendation
   - Third recommendation

4. Conclusion
   This is a comprehensive conclusion.
"""
    
    # Print each line with a small delay to simulate streaming
    for line in report.split('\n'):
        print(line)
        time.sleep(0.1)
    
    # Print the end marker
    print("==================================================\n")
    
    # Print completion message
    print("✅ Research complete!")

if __name__ == "__main__":
    main()