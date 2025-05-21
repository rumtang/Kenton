# Tool: File Search - Uses OpenAI's native vector store capability for o3-responses
# IMPORTANT: This implementation works with the OpenAI Agents SDK v1.30+
# Last updated: 2025-05-19

import os
import logging
from tools.errors import create_vector_store_error

logger = logging.getLogger(__name__)

# Clean environment at module import time
def _clean_env_var(var_name):
    """Clean a single environment variable from problematic characters."""
    if var_name in os.environ:
        value = os.environ[var_name]
        if '…' in value or '\u2026' in value:
            # Try to extract the actual key part before the ellipsis
            if 'sk-' in value:
                # For API keys, keep the sk- prefix and some trailing chars
                clean_value = value.split('…')[0]
                os.environ[var_name] = clean_value
                logger.info(f"Cleaned {var_name} environment variable")
            else:
                del os.environ[var_name]
                logger.info(f"Removed problematic {var_name} environment variable")

# Clean problematic vars
_clean_env_var('OPENAI_API_KEY')
_clean_env_var('VECTOR_STORE_ID')
_clean_env_var('OPENAI_VECTOR_STORE_ID')

# Note on API Usage:
# - For attachments to specific files in the OpenAI API, use 'file_id' (singular)
# - For vector search, use 'vector_store_ids' (plural) as an array
# - Do not use 'file_id: None' - either provide a valid ID or omit the parameter

from agents import function_tool
from openai import OpenAI
import json

@function_tool
def file_search(query: str) -> str:
    """
    Search through vectorized documents using OpenAI's file search capability.
    Returns results with inline citations formatted for o3-responses.
    """
    
    # Get vector store ID from environment
    vector_store_id = os.getenv("VECTOR_STORE_ID") or os.getenv("OPENAI_VECTOR_STORE_ID")
    
    if not vector_store_id:
        return "Error: VECTOR_STORE_ID not found in environment. Please set it in your .env file."
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a query message for file search
        thread = client.beta.threads.create()
        
        # Create a query message without file attachments
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
            # No attachments needed for vector store search
        )
        
        # Run the thread with file search
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_file_search",  # Placeholder assistant ID
            additional_instructions="Search the vector store for relevant information.",
            tools=[{"type": "file_search"}],
            tool_choice={"type": "file_search"},
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]  # Must be an array as per API requirements
                }
            }
        )
        
        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        
        # Get messages with citations
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        # Format results with citations
        results = []
        for msg in messages:
            if msg.role == "assistant":
                content = msg.content[0].text.value
                
                # Extract annotations (citations)
                annotations = msg.content[0].text.annotations if hasattr(msg.content[0].text, 'annotations') else []
                
                if annotations:
                    # Format with inline citations
                    for ann in annotations:
                        if ann.type == "file_citation":
                            citation_text = f"[{ann.file_citation.file_id}:{ann.text}]"
                            content = content.replace(ann.text, citation_text)
                
                results.append(content)
        
        # Return formatted results
        if results:
            return "\n\n".join(results)
        else:
            return "No results found in vector store for query: " + query
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"File search error: {error_message}")
        
        # Use our new error handling system to generate rich diagnostics
        error = create_vector_store_error(error_message, {
            "query": query,
            "vector_store_id": vector_store_id
        })
        
        # Return formatted error message
        return str(error)

# For backward compatibility with existing code
def get_file_search_tool():
    """Legacy function - file search is now a function tool for o3-responses."""
    # Return None since o3-responses doesn't support FileSearchTool
    return None