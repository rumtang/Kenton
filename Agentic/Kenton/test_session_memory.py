#!/usr/bin/env python3
"""
Test script to check if session memory is working properly
"""

import sys
import os
from pathlib import Path

# Setup environment
script_dir = Path(__file__).parent.absolute()
env_file = script_dir / ".env"

# Load environment
from dotenv import load_dotenv
load_dotenv(env_file, override=True)

# Import components
from agent_config import session_manager, get_agent
import asyncio
from agents import Runner

async def test_session_memory():
    """Test session memory functionality"""
    print("🧪 Testing Session Memory Functionality")
    print("="*60)
    
    # Test 1: Basic SessionManager functionality
    print("\n1️⃣ Testing SessionManager:")
    session_id = "test_session_123"
    
    # Add some test data
    session_manager.add_to_session(session_id, "What is Microsoft doing?", "Microsoft is focusing on AI...")
    session_manager.add_to_session(session_id, "Tell me more about their strategy", "Their strategy involves...")
    
    # Get session context
    context = session_manager.get_session_context(session_id)
    print(f"Session context:\n{context}")
    
    # Check session data
    session = session_manager.get_session(session_id)
    print(f"\nSession history count: {len(session['history'])}")
    print(f"Last query: {session['history'][-1]['query']}")
    
    # Test 2: Agent with session context
    print("\n\n2️⃣ Testing Agent with Session Context:")
    
    # Create agent with session context
    agent = get_agent(model="gpt-4.1-mini", session_context=context)
    
    # Test query that should use context
    test_query = "What was I asking about?"
    print(f"Test query: {test_query}")
    
    try:
        result = await Runner.run(agent, test_query)
        
        if hasattr(result, 'final_output'):
            response = result.final_output
        elif hasattr(result, 'content'):
            response = result.content
        else:
            response = str(result)
            
        print(f"\nAgent response: {response[:200]}...")
        
        # Check if response references previous context
        context_words = ["Microsoft", "strategy", "AI"]
        context_found = any(word.lower() in response.lower() for word in context_words)
        print(f"\n✅ Context reference found: {context_found}")
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
    
    # Test 3: Check ConversationManager (if available)
    print("\n\n3️⃣ Testing ConversationManager:")
    try:
        from conversation_manager import get_conversation_manager
        conv_manager = get_conversation_manager()
        
        # Add test entry
        conv_manager.add_entry(
            session_id="test_conv_123",
            query="What about Tesla?",
            response="Tesla is developing...",
            model="gpt-4.1"
        )
        
        # Get history
        history = conv_manager.get_history("test_conv_123")
        print(f"Conversation history entries: {len(history)}")
        
        # Get formatted history
        formatted = conv_manager.get_formatted_history("test_conv_123")
        print(f"Formatted history:\n{formatted}")
        
        # Get summary
        summary = conv_manager.get_session_summary("test_conv_123")
        print(f"\nSession summary: {summary}")
        
    except Exception as e:
        print(f"⚠️ ConversationManager not available: {e}")
    
    print("\n" + "="*60)
    print("✅ Session memory test complete")

if __name__ == "__main__":
    asyncio.run(test_session_memory())