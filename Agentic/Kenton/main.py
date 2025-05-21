# Main entry point: Launches the agent with a sample query

import sys
import os
import argparse

# Clean problematic environment variables BEFORE any imports
def clean_environment():
    """Remove or clean environment variables with problematic encoding."""
    # Only clean variables that have encoding issues, not valid API keys
    problematic_vars = ['OPENAI_BASE_URL', 'OPENAI_DEPLOYMENT', 'VECTOR_STORE_ID']
    
    for var in problematic_vars:
        if var in os.environ:
            value = os.environ[var]
            # Check for problematic characters
            if '…' in value or '\u2026' in value:
                del os.environ[var]
                print(f"[Info] Removed {var} due to encoding issues")
    
    # Special handling for API key - only remove if it's corrupted
    if 'OPENAI_API_KEY' in os.environ:
        api_key = os.environ['OPENAI_API_KEY']
        if '…' in api_key or '\u2026' in api_key or len(api_key) < 50:
            del os.environ['OPENAI_API_KEY']
            print(f"[Info] Removed corrupted OPENAI_API_KEY")

# Clean environment first
clean_environment()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from agent_config import get_agent
from agents import Runner

# Load environment variables from .env file (will reload cleaned vars)
load_dotenv(override=True)

def run_agent(query, model='gpt-4.1'):
    """Run the Deep Research agent with the specified query and model
    
    This function can be called programmatically or from the command line.
    It returns the agent's response.
    """
    # Initialize the agent with configuration
    print(f"Initializing Deep Research Agent with {model}...")
    agent = get_agent(model=model)
    
    print(f"\n🔬 Starting research on: {query}\n")
    
    try:
        # Run the agent synchronously
        result = Runner.run_sync(agent, query)
        
        # Print the final output
        print("\n📊 Final Research Report:\n")
        print("=" * 50)
        print(result.final_output)
        print("=" * 50)
        
        # Return the result for programmatic use
        return result.final_output
        
    except Exception as e:
        error_msg = f"\n❌ Error running agent: {e}"
        print(error_msg)
        return error_msg
    finally:
        print("\n✅ Research complete!")

def main():
    """Main function to run the Deep Research agent from the command line"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deep Research Agent")
    parser.add_argument('--vector-store-id', help='Vector store ID (overrides env variable)')
    parser.add_argument('--model', default='gpt-4.1', help='Model to use (default: gpt-4.1)')
    parser.add_argument('--query', help='Research query to process')
    args = parser.parse_args()
    
    # Set vector store ID if provided
    if args.vector_store_id:
        os.environ['OPENAI_VECTOR_STORE_ID'] = args.vector_store_id
    
    # Get query from arguments or prompt the user
    user_prompt = args.query
    if not user_prompt:
        try:
            user_prompt = input("Tell me what you want to explore: ").strip()
            if not user_prompt:
                user_prompt = "Research the impact of generative AI on marketing."
                print(f"Using default prompt: {user_prompt}")
        except (EOFError, KeyboardInterrupt):
            user_prompt = "Research the impact of generative AI on marketing."
            print(f"\nUsing default prompt: {user_prompt}")
    
    # Run the agent
    run_agent(user_prompt, args.model)

if __name__ == "__main__":
    main()