# Test CLI-Web consistency
# Verifies that CLI and web interfaces produce consistent results

import sys
import os
import json
import subprocess
import requests
from pathlib import Path

# Get the project root directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent

# Add the project root to the Python path
sys.path.insert(0, str(project_root))

# Import the run_agent function from main.py
from main import run_agent

def run_cli_query(query, model="o3"):
    """Run a query using the direct CLI function"""
    result = run_agent(query, model)
    return result

def run_web_query(query, model="o3"):
    """Run a query using the web API"""
    # Start a simple web server for testing
    server_process = subprocess.Popen(
        ["uvicorn", "enhanced_api_server:app", "--port", "8901"],
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for the server to start
        import time
        time.sleep(3)
        
        # Call the API
        response = requests.post(
            "http://localhost:8901/api/research",
            json={"query": query, "model": model},
            stream=True,
            timeout=300  # 5-minute timeout
        )
        
        # Process the streaming response
        content = ""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data = json.loads(line_text[6:])
                    if data.get('type') == 'content' and 'data' in data:
                        content += data['data']
        
        return content
    finally:
        # Always terminate the server when done
        server_process.terminate()

def test_cli_web_consistency():
    """Test that CLI and web interfaces produce consistent results"""
    # Use a simple query for fast testing
    query = "What is the weather in New York?"
    model = "o3-mini"  # Use a smaller model for faster testing
    
    print(f"Testing consistency with query: '{query}'")
    
    # Run through CLI
    print("Running CLI query...")
    cli_result = run_cli_query(query, model)
    print(f"CLI result length: {len(cli_result)} characters")
    
    # Run through web API
    print("Running web API query...")
    web_result = run_web_query(query, model)
    print(f"Web result length: {len(web_result)} characters")
    
    # Compare the results
    # Note: There might be slight formatting differences, so we check:
    # 1. Similar length (within 10%)
    # 2. Similar content (key phrases appear in both)
    length_ratio = len(cli_result) / max(1, len(web_result))
    
    print(f"Length ratio: {length_ratio:.2f}")
    print("Passed length check:", 0.9 <= length_ratio <= 1.1)
    
    # Extract key words from the CLI result (simplistic approach)
    cli_words = set(w.lower() for w in cli_result.split() if len(w) > 5)
    web_words = set(w.lower() for w in web_result.split() if len(w) > 5)
    
    common_words = cli_words.intersection(web_words)
    similarity = len(common_words) / max(1, len(cli_words.union(web_words)))
    
    print(f"Content similarity: {similarity:.2f}")
    print("Passed content check:", similarity >= 0.7)
    
    # Overall pass/fail
    is_consistent = (0.9 <= length_ratio <= 1.1) and (similarity >= 0.7)
    print("CONSISTENCY TEST:", "PASSED" if is_consistent else "FAILED")
    
    return is_consistent

if __name__ == "__main__":
    test_cli_web_consistency()