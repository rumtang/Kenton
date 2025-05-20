"""
Centralized error handling for AI agent tools with diagnostic information.

This module provides structured error classes with rich context for easier debugging
and self-explanatory error messages that guide users to solutions.
"""

import logging
import inspect
import traceback
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AgentExecutionError(Exception):
    """
    Rich diagnostic error class for agent tools.
    
    This exception provides context-aware error information including:
    - Error code for categorization
    - Hint about what likely went wrong
    - Resolution steps to fix the issue
    - Source information (file, function, line)
    - Technical details for debugging
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        hint: Optional[str] = None, 
        resolution: Optional[str] = None,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code or "AGENT-E000"  # Default generic error code
        self.hint = hint
        self.resolution = resolution
        
        # Capture source information if not provided
        if source is None:
            frame = inspect.currentframe()
            if frame:
                try:
                    frame = frame.f_back  # Get the caller's frame
                    if frame:
                        filename = frame.f_code.co_filename
                        function = frame.f_code.co_name
                        lineno = frame.f_lineno
                        self.source = f"{filename}:{function}:{lineno}"
                    else:
                        self.source = "unknown"
                finally:
                    del frame
        else:
            self.source = source
            
        self.details = details or {}
        
        # Log the error
        self._log_error()
    
    def _log_error(self):
        """Log detailed error information."""
        logger.error(
            f"ERROR {self.code}: {str(self)} | "
            f"Source: {self.source} | "
            f"Hint: {self.hint or 'N/A'}"
        )
        
    def __str__(self):
        """Format the error message with diagnostic information."""
        lines = [f"ERROR-{self.code}: {super().__str__()}"]
        
        if self.hint:
            lines.append(f"- Problem: {self.hint}")
        
        lines.append(f"- Source: {self.source}")
        
        if self.resolution:
            lines.append(f"- Solution: {self.resolution}")
            
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            lines.append(f"- Details: {details_str}")
            
        return "\n".join(lines)

# Vector store specific errors
class FileSearchError(AgentExecutionError):
    """Errors related to file search and vector store operations."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        hint: Optional[str] = None, 
        resolution: Optional[str] = None,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        # Default to FS prefix if no specific code provided
        if code is None or not code.startswith("FS"):
            code = f"FS{code}" if code else "FS000"
            
        super().__init__(message, code, hint, resolution, source, details)

# Common error factory functions
def create_api_key_error(service_name: str, details: Optional[Dict[str, Any]] = None):
    """Create an error for API key issues."""
    return AgentExecutionError(
        message=f"{service_name.upper()} API key error",
        code="AUTH001",
        hint=f"Missing or invalid {service_name} API key",
        resolution=f"Check your .env file for a valid {service_name.upper()}_API_KEY",
        details=details
    )

def create_network_error(service_name: str, original_error: Exception):
    """Create an error for network/connectivity issues."""
    return AgentExecutionError(
        message=f"Network error connecting to {service_name}: {str(original_error)}",
        code="NET001",
        hint="Network connectivity issue or service unavailability",
        resolution="Check your internet connection and service status",
        details={"original_error": str(original_error)}
    )

def create_vector_store_error(error_message: str, details: Optional[Dict[str, Any]] = None):
    """Create a specific file search / vector store error."""
    
    # Identify common vector store error patterns
    if "vector_store_id" in error_message.lower():
        return FileSearchError(
            message=error_message,
            code="FS001",
            hint="Vector store ID missing or invalid",
            resolution="Set OPENAI_VECTOR_STORE_ID in your .env file",
            details=details
        )
    elif "file_id" in error_message.lower() and "attachments" in error_message.lower():
        return FileSearchError(
            message=error_message,
            code="FS002",
            hint="Incorrect file attachment parameters",
            resolution="Use file_id (singular) for attachments or omit attachments for vector store search",
            details=details
        )
    else:
        return FileSearchError(
            message=error_message,
            code="FS999",
            hint="Unknown vector store error",
            resolution="Check logs for detailed error messages and verify API compatibility",
            details=details
        )