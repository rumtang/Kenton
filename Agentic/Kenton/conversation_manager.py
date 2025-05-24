"""
Conversation History Management for Kenton Deep Research Agent
Supports both Redis (for production) and in-memory storage (for development)
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict, OrderedDict

# Try to import redis, but don't fail if it's not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, using in-memory storage")

@dataclass
class ConversationEntry:
    """Represents a single conversation exchange"""
    timestamp: float
    query: str
    response: str
    model: str = "gpt-4.1"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEntry':
        """Create from dictionary"""
        return cls(**data)

class ConversationManager:
    """Manages conversation history with automatic fallback"""
    
    def __init__(self, 
                 redis_url: Optional[str] = None,
                 max_history: int = 10,
                 ttl_hours: int = 24):
        """
        Initialize conversation manager
        
        Args:
            redis_url: Redis connection URL (optional)
            max_history: Maximum number of exchanges to keep per session
            ttl_hours: Time to live for conversations in hours
        """
        self.max_history = max_history
        self.ttl_seconds = ttl_hours * 3600
        self.use_redis = False
        self.redis_client = None
        
        # Try to setup Redis if available and URL provided
        if REDIS_AVAILABLE and (redis_url or os.getenv('REDIS_URL')):
            try:
                url = redis_url or os.getenv('REDIS_URL')
                self.redis_client = redis.from_url(url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                logging.info("Connected to Redis for conversation storage")
            except Exception as e:
                logging.warning(f"Failed to connect to Redis: {e}. Using in-memory storage.")
                self.use_redis = False
        
        # Fallback to in-memory storage
        if not self.use_redis:
            self.memory_store: Dict[str, List[ConversationEntry]] = defaultdict(list)
            self.memory_timestamps: Dict[str, float] = {}
            logging.info("Using in-memory conversation storage")
    
    def add_entry(self, session_id: str, query: str, response: str, 
                  model: str = "gpt-4.1", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a conversation entry"""
        entry = ConversationEntry(
            timestamp=time.time(),
            query=query,
            response=response,
            model=model,
            metadata=metadata or {}
        )
        
        if self.use_redis:
            self._add_redis_entry(session_id, entry)
        else:
            self._add_memory_entry(session_id, entry)
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationEntry]:
        """Get conversation history for a session"""
        if self.use_redis:
            return self._get_redis_history(session_id, limit)
        else:
            return self._get_memory_history(session_id, limit)
    
    def get_formatted_history(self, session_id: str, limit: Optional[int] = None) -> str:
        """Get formatted conversation history as a string"""
        history = self.get_history(session_id, limit)
        if not history:
            return ""
        
        formatted = []
        for entry in history:
            timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
            formatted.append(f"[{timestamp}] User: {entry.query}")
            formatted.append(f"[{timestamp}] Assistant: {entry.response[:200]}...")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def clear_session(self, session_id: str) -> None:
        """Clear history for a specific session"""
        if self.use_redis:
            self.redis_client.delete(f"conversation:{session_id}")
        else:
            self.memory_store.pop(session_id, None)
            self.memory_timestamps.pop(session_id, None)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a session"""
        history = self.get_history(session_id)
        if not history:
            return {
                "session_id": session_id,
                "total_exchanges": 0,
                "start_time": None,
                "last_activity": None,
                "topics": []
            }
        
        return {
            "session_id": session_id,
            "total_exchanges": len(history),
            "start_time": datetime.fromtimestamp(history[0].timestamp).isoformat(),
            "last_activity": datetime.fromtimestamp(history[-1].timestamp).isoformat(),
            "duration_minutes": int((history[-1].timestamp - history[0].timestamp) / 60),
            "models_used": list(set(entry.model for entry in history)),
            "topics": self._extract_topics(history)
        }
    
    # Private Redis methods
    def _add_redis_entry(self, session_id: str, entry: ConversationEntry) -> None:
        """Add entry using Redis"""
        key = f"conversation:{session_id}"
        
        # Get existing history
        data = self.redis_client.get(key)
        history = json.loads(data) if data else []
        
        # Add new entry
        history.append(entry.to_dict())
        
        # Trim to max history
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        # Store with TTL
        self.redis_client.setex(
            key,
            self.ttl_seconds,
            json.dumps(history)
        )
    
    def _get_redis_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationEntry]:
        """Get history from Redis"""
        key = f"conversation:{session_id}"
        data = self.redis_client.get(key)
        
        if not data:
            return []
        
        history = [ConversationEntry.from_dict(item) for item in json.loads(data)]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    # Private in-memory methods
    def _add_memory_entry(self, session_id: str, entry: ConversationEntry) -> None:
        """Add entry using in-memory storage"""
        # Clean old sessions periodically
        self._clean_old_sessions()
        
        # Add entry
        self.memory_store[session_id].append(entry)
        self.memory_timestamps[session_id] = time.time()
        
        # Trim to max history
        if len(self.memory_store[session_id]) > self.max_history:
            self.memory_store[session_id] = self.memory_store[session_id][-self.max_history:]
    
    def _get_memory_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationEntry]:
        """Get history from in-memory storage"""
        history = self.memory_store.get(session_id, [])
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def _clean_old_sessions(self) -> None:
        """Remove old sessions from memory"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, last_activity in self.memory_timestamps.items():
            if current_time - last_activity > self.ttl_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.memory_store.pop(session_id, None)
            self.memory_timestamps.pop(session_id, None)
    
    def _extract_topics(self, history: List[ConversationEntry]) -> List[str]:
        """Extract main topics from conversation history"""
        topics = []
        
        # Simple keyword extraction from queries
        keywords = set()
        for entry in history:
            # Extract capitalized words and phrases
            words = entry.query.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 3:
                    keywords.add(word)
                    # Check for multi-word entities
                    if i < len(words) - 1 and words[i + 1][0].isupper():
                        keywords.add(f"{word} {words[i + 1]}")
        
        topics = list(keywords)[:5]  # Top 5 topics
        return topics

# Global instance for easy access
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get or create the global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager