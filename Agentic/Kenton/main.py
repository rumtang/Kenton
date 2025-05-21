# Main entry point: Launches the agent with a sample query

import sys
import os
import argparse

# Clean problematic environment variables BEFORE any imports
def clean_environment():
    """Remove or clean environment variables with problematic encoding."""
    # Only clean variables that have encoding issues
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
        # Check for problematic characters but allow project-scoped keys which are longer
        if '…' in api_key or '\u2026' in api_key:
            del os.environ['OPENAI_API_KEY']
            print(f"[Info] Removed corrupted OPENAI_API_KEY")
        # Don't check length here as project-scoped keys are longer

# Clean environment first
clean_environment()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from agent_config import get_agent
from agents import Runner

# Load environment variables from .env file (will reload cleaned vars)
load_dotenv(override=True)

def run_agent(query, model='gpt-4.1', enable_reasoning=False):
    """Run the Deep Research agent with the specified query and model
    
    This function can be called programmatically or from the command line.
    It returns the agent's response.
    
    Args:
        query (str): The research query to process
        model (str): The model to use, e.g. 'gpt-4.1', 'o3', 'o3-mini'
        enable_reasoning (bool): Whether to enable reasoning capabilities
    
    Returns:
        str: The agent's final response
    """
    # Initialize the agent with configuration and pass query for reasoning effort determination
    reasoning_status = "with reasoning" if enable_reasoning else "in standard mode"
    print(f"Initializing Deep Research Agent with {model} {reasoning_status}...")
    agent = get_agent(model=model, enable_reasoning=enable_reasoning, query=query)
    
    print(f"\n🔬 Starting research on: {query}\n")
    
    try:
        # Run the agent synchronously
        result = Runner.run_sync(agent, query)
        
        # Print reasoning trace if available
        if enable_reasoning:
            reasoning_trace = None
            # Check various property names that might contain reasoning
            for attr in ['reasoning_trace', 'reasoning', 'trace']:
                if hasattr(result, attr) and getattr(result, attr):
                    reasoning_trace = getattr(result, attr)
                    break
                    
            if reasoning_trace:
                print("\n🧠 Reasoning Process:\n")
                print("-" * 50)
                print(reasoning_trace)
                print("-" * 50)
        
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
    parser.add_argument('--reasoning', action='store_true', help='Enable reasoning capabilities')
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
    
    # Run the agent with or without reasoning
    run_agent(user_prompt, args.model, enable_reasoning=args.reasoning)

if __name__ == "__main__":
    main()