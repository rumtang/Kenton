#!/usr/bin/env python3
"""
Enhanced CLI with session management, thinking display, and continuous conversation
"""

import sys
import os
import uuid
from datetime import datetime
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

# Import after environment is set up
from agent_config import get_agent, session_manager, get_current_date_context
from agents import Runner
import asyncio

class EnhancedCLI:
    """Enhanced CLI with session management and thinking display."""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.agent = None
        self.show_thinking = True
        self.model = "gpt-4.1"
        
    def display_banner(self):
        """Display welcome banner with current date."""
        date_context = get_current_date_context()
        print("=" * 80)
        print("🔬 KENTON DEEP RESEARCH AGENT - Enhanced CLI")
        print("=" * 80)
        print(f"📅 Current Date: {date_context['current_date']}")
        print(f"📊 Current Quarter: {date_context['current_quarter']} {date_context['current_year']}")
        print(f"🏢 Fiscal Year: FY{date_context['fiscal_year']}")
        print(f"🆔 Session ID: {self.session_id}")
        print("=" * 80)
        print("I'm your strategic research advisor. I help executives understand")
        print("how technological and market trends impact their organizations.")
        print()
        print("Commands:")
        print("  /help     - Show this help message")
        print("  /thinking - Toggle thinking display on/off")
        print("  /model    - Change AI model")
        print("  /session  - Show session info")
        print("  /clear    - Clear session history")
        print("  /quit     - Exit the application")
        print("=" * 80)
        print()
    
    def display_thinking(self, message):
        """Display thinking process if enabled."""
        if self.show_thinking:
            print(f"🧠 [THINKING] {message}")
    
    def handle_command(self, user_input):
        """Handle special commands."""
        command = user_input.lower().strip()
        
        if command == "/help":
            self.display_banner()
            return True
            
        elif command == "/thinking":
            self.show_thinking = not self.show_thinking
            status = "ON" if self.show_thinking else "OFF"
            print(f"💭 Thinking display is now {status}")
            return True
            
        elif command == "/model":
            print("Available models:")
            print("  1. gpt-4.1 (default)")
            print("  2. gpt-4.1-mini")
            print("  3. o3")
            print("  4. o3-mini")
            choice = input("Select model (1-4): ").strip()
            models = {"1": "gpt-4.1", "2": "gpt-4.1-mini", "3": "o3", "4": "o3-mini"}
            if choice in models:
                self.model = models[choice]
                self.agent = None  # Reset agent to use new model
                print(f"🤖 Model changed to {self.model}")
            else:
                print("❌ Invalid selection")
            return True
            
        elif command == "/session":
            session = session_manager.get_session(self.session_id)
            print(f"🆔 Session ID: {self.session_id}")
            print(f"📅 Created: {session['created_at']}")
            print(f"💬 Messages: {len(session['history'])}")
            if session['history']:
                print("📜 Recent topics:")
                for item in session['history'][-3:]:
                    print(f"   • {item['query'][:50]}...")
            return True
            
        elif command == "/clear":
            if self.session_id in session_manager.sessions:
                del session_manager.sessions[self.session_id]
            self.session_id = str(uuid.uuid4())
            print(f"🗑️ Session cleared. New session ID: {self.session_id}")
            return True
            
        elif command in ["/quit", "/exit"]:
            print("👋 Thanks for using Kenton Deep Research Agent!")
            return "quit"
            
        return False
    
    async def process_query(self, query):
        """Process a research query with thinking display."""
        try:
            # Initialize agent if not already done
            if not self.agent:
                self.display_thinking("Initializing research agent...")
                session_context = session_manager.get_session_context(self.session_id)
                self.agent = get_agent(model=self.model, session_context=session_context)
                self.display_thinking(f"Agent initialized with {self.model}")
            
            # Show research process
            self.display_thinking("Analyzing query and selecting appropriate tools...")
            self.display_thinking("Executing research plan...")
            
            # Run the agent
            print("🔍 Researching...")
            result = await Runner.run(self.agent, query)
            
            # Extract and display result
            if hasattr(result, 'final_output'):
                response = result.final_output
            elif hasattr(result, 'content'):
                response = result.content
            else:
                response = str(result)
            
            # Store in session
            session_manager.add_to_session(self.session_id, query, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def format_response(self, response):
        """Format the response for display."""
        print("\n" + "=" * 80)
        print("📊 RESEARCH RESULTS")
        print("=" * 80)
        print(response)
        print("=" * 80)
    
    async def run_conversation(self):
        """Run the main conversation loop."""
        self.display_banner()
        
        while True:
            try:
                # Get user input
                print("\n" + "🔸" * 40)
                user_input = input("💼 Your strategic question: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                command_result = self.handle_command(user_input)
                if command_result == "quit":
                    break
                elif command_result:
                    continue
                
                # Process research query
                response = await self.process_query(user_input)
                self.format_response(response)
                
                # Ask for follow-up
                print("\n💡 Ask a follow-up question, explore related topics, or use commands:")
                print("   📝 Continue the conversation naturally")
                print("   ⚙️  Type /help for commands")
                print("   🚪 Type /quit to exit")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using Kenton Deep Research Agent!")
                break
            except EOFError:
                print("\n\n👋 Thanks for using Kenton Deep Research Agent!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("🔄 Continuing conversation...")

def main():
    """Main function to run the Enhanced CLI."""
    print("🚀 Starting Enhanced Kenton Deep Research Agent...")
    
    # Create and run CLI
    cli = EnhancedCLI()
    
    # Run the conversation loop
    try:
        asyncio.run(cli.run_conversation())
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Kenton Deep Research Agent!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()