"""
Memory provider for the agentstable SDK.

This module provides functionality for storing and retrieving memory using Redis.
"""

import os
import json
from typing import Dict, List, Optional, Union, Any, Generator, Callable
import importlib.util
from datetime import datetime

class MemoryProvider:
    """
    Provider for memory storage and retrieval using Redis.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the Memory provider with Redis.
        
        Args:
            redis_url: The Redis connection URL. If not provided, it will look for REDIS_URL in environment variables.
        """
        self.redis_url = redis_url or os.environ.get("REDIS_URL")
        self.redis_available = importlib.util.find_spec("redis") is not None
        self._redis = None
        self._redis_client = None
        
        if self.redis_available and self.redis_url:
            try:
                import redis
                self._redis = redis
                self._redis_client = redis.from_url(self.redis_url)
                self._redis_client.ping()  # Test the connection
            except (ImportError, Exception) as e:
                self.redis_available = False
                print(f"Redis connection failed: {e}")
    
    @property
    def is_available(self) -> bool:
        """
        Check if Redis is available and connected.
        
        Returns:
            bool: True if Redis is available and connected, False otherwise.
        """
        return self.redis_available and self._redis_client is not None
    
    def store(self, key: str, value: Any, namespace: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """
        Store a value in Redis.
        
        Args:
            key: The key to store the value under
            value: The value to store (will be JSON serialized)
            namespace: Optional namespace prefix for the key
            ttl: Optional time-to-live in seconds
            
        Returns:
            bool: True if the value was stored, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            # Add namespace prefix if provided
            full_key = f"{namespace}:{key}" if namespace else key
            
            # JSON serialize the value
            json_value = json.dumps(value)
            
            # Store in Redis
            if ttl:
                return bool(self._redis_client.setex(full_key, ttl, json_value))
            else:
                return bool(self._redis_client.set(full_key, json_value))
        except Exception as e:
            print(f"Error storing value: {e}")
            return False
    
    def retrieve(self, key: str, namespace: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve a value from Redis.
        
        Args:
            key: The key to retrieve the value from
            namespace: Optional namespace prefix for the key
            
        Returns:
            Any: The retrieved value, or None if not found
        """
        if not self.is_available:
            return None
        
        try:
            # Add namespace prefix if provided
            full_key = f"{namespace}:{key}" if namespace else key
            
            # Get from Redis
            value = self._redis_client.get(full_key)
            
            if value is None:
                return None
            
            # JSON deserialize the value
            return json.loads(value)
        except Exception as e:
            print(f"Error retrieving value: {e}")
            return None
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Delete a value from Redis.
        
        Args:
            key: The key to delete
            namespace: Optional namespace prefix for the key
            
        Returns:
            bool: True if the value was deleted, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            # Add namespace prefix if provided
            full_key = f"{namespace}:{key}" if namespace else key
            
            # Delete from Redis
            return bool(self._redis_client.delete(full_key))
        except Exception as e:
            print(f"Error deleting value: {e}")
            return False
    
    def add_to_list(self, key: str, value: Any, namespace: Optional[str] = None, max_length: Optional[int] = None) -> bool:
        """
        Add a value to a list in Redis.
        
        Args:
            key: The key of the list
            value: The value to add to the list (will be JSON serialized)
            namespace: Optional namespace prefix for the key
            max_length: Optional maximum length of the list
            
        Returns:
            bool: True if the value was added, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            # Add namespace prefix if provided
            full_key = f"{namespace}:{key}" if namespace else key
            
            # JSON serialize the value
            json_value = json.dumps(value)
            
            # Use a pipeline for atomicity
            with self._redis_client.pipeline() as pipe:
                # Add to the list
                pipe.lpush(full_key, json_value)
                
                # Trim the list if max_length is specified
                if max_length is not None:
                    pipe.ltrim(full_key, 0, max_length - 1)
                
                # Execute the pipeline
                pipe.execute()
            
            return True
        except Exception as e:
            print(f"Error adding to list: {e}")
            return False
    
    def get_list(self, key: str, namespace: Optional[str] = None, start: int = 0, end: int = -1) -> List[Any]:
        """
        Get a list from Redis.
        
        Args:
            key: The key of the list
            namespace: Optional namespace prefix for the key
            start: Start index
            end: End index (-1 for all)
            
        Returns:
            List[Any]: The list values
        """
        if not self.is_available:
            return []
        
        try:
            # Add namespace prefix if provided
            full_key = f"{namespace}:{key}" if namespace else key
            
            # Get the list from Redis
            values = self._redis_client.lrange(full_key, start, end)
            
            # JSON deserialize the values
            return [json.loads(v) for v in values]
        except Exception as e:
            print(f"Error getting list: {e}")
            return []

    def store_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a conversation message.
        
        Args:
            conversation_id: Identifier for the conversation
            role: Role of the message sender (e.g., 'user', 'assistant')
            content: Message content
            metadata: Optional metadata for the message
            
        Returns:
            bool: True if the message was stored, False otherwise
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        return self.add_to_list(f"conversation:{conversation_id}", message, namespace="memory")
    
    def get_conversation(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: Identifier for the conversation
            limit: Optional limit on the number of messages to retrieve
            
        Returns:
            List[Dict[str, Any]]: The conversation messages
        """
        end = limit - 1 if limit is not None else -1
        return self.get_list(f"conversation:{conversation_id}", namespace="memory", start=0, end=end)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear all messages from a conversation.
        
        Args:
            conversation_id: Identifier for the conversation
            
        Returns:
            bool: True if the conversation was cleared, False otherwise
        """
        return self.delete(f"conversation:{conversation_id}", namespace="memory")

# Create a singleton instance with environment variable
memory_provider = MemoryProvider()

# Convenience functions for external use
def store(key: str, value: Any, namespace: Optional[str] = None, ttl: Optional[int] = None) -> bool:
    """Store a value in memory."""
    return memory_provider.store(key, value, namespace, ttl)

def retrieve(key: str, namespace: Optional[str] = None) -> Optional[Any]:
    """Retrieve a value from memory."""
    return memory_provider.retrieve(key, namespace)

def delete(key: str, namespace: Optional[str] = None) -> bool:
    """Delete a value from memory."""
    return memory_provider.delete(key, namespace)

def store_message(conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Store a conversation message."""
    return memory_provider.store_message(conversation_id, role, content, metadata)

def get_conversation(conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get messages from a conversation."""
    return memory_provider.get_conversation(conversation_id, limit)

def clear_conversation(conversation_id: str) -> bool:
    """Clear all messages from a conversation."""
    return memory_provider.clear_conversation(conversation_id) 