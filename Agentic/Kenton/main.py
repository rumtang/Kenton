# Main entry point: Launches the agent with a sample query

import sys
import os
import argparse

# Clean problematic environment variables BEFORE any imports
def clean_environment():
    """Remove or clean environment variables with problematic encoding."""
    problematic_vars = ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_DEPLOYMENT', 
                       'VECTOR_STORE_ID', 'OPENAI_VECTOR_STORE_ID']
    
    for var in problematic_vars:
        if var in os.environ:
            value = os.environ[var]
            # Check for problematic characters
            if '…' in value or '\u2026' in value:
                del os.environ[var]
                print(f"[Info] Removed {var} due to encoding issues")

# Clean environment first
clean_environment()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from agent_config import get_agent
from agents import Runner

# Load environment variables from .env file (will reload cleaned vars)
load_dotenv(override=True)

def main():
    """Main function to run the Deep Research agent"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deep Research Agent")
    parser.add_argument('--vector-store-id', help='Vector store ID (overrides env variable)')
    parser.add_argument('--model', default='o3', help='Model to use (default: o3)')
    args = parser.parse_args()
    
    # Set vector store ID if provided
    if args.vector_store_id:
        os.environ['VECTOR_STORE_ID'] = args.vector_store_id
    
    # Initialize the agent with configuration
    print(f"Initializing Deep Research Agent with {args.model}...")
    agent = get_agent(model=args.model)
    
    # Get user input or use default prompt
    try:
        user_prompt = input("Enter your research question: ").strip()
        if not user_prompt:
            user_prompt = "Research the impact of generative AI on marketing."
            print(f"Using default prompt: {user_prompt}")
    except (EOFError, KeyboardInterrupt):
        user_prompt = "Research the impact of generative AI on marketing."
        print(f"\nUsing default prompt: {user_prompt}")
    
    print(f"\n🔬 Starting research on: {user_prompt}\n")
    
    try:
        # Run the agent synchronously
        result = Runner.run_sync(agent, user_prompt)
        
        # Print the final output
        print("\n📊 Final Research Report:\n")
        print("=" * 50)
        print(result.final_output)
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")
        
    print("\n✅ Research complete!")

if __name__ == "__main__":
    main()