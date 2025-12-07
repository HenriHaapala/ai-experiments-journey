"""
Conversation memory management using Redis
Stores conversation history for context-aware agent responses
"""
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history using Redis
    Stores messages with timestamps and provides context retrieval
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis connection

        Args:
            redis_url: Redis connection URL (default: from env or localhost)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fallback to in-memory storage
            self.redis_client = None
            self._memory_fallback = {}
            logger.warning("Using in-memory fallback for conversation storage")

    def _get_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation"""
        return f"conversation:{conversation_id}"

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a message to conversation history

        Args:
            conversation_id: Unique conversation identifier
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata (tool calls, timestamps, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        key = self._get_key(conversation_id)

        if self.redis_client:
            try:
                # Append to list in Redis
                self.redis_client.rpush(key, json.dumps(message))
                # Set expiration to 7 days
                self.redis_client.expire(key, 60 * 60 * 24 * 7)
                logger.debug(f"Added message to conversation {conversation_id}")
            except RedisError as e:
                logger.error(f"Redis error adding message: {e}")
        else:
            # Fallback to in-memory
            if conversation_id not in self._memory_fallback:
                self._memory_fallback[conversation_id] = []
            self._memory_fallback[conversation_id].append(message)

    def get_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve conversation history

        Args:
            conversation_id: Unique conversation identifier
            limit: Maximum number of recent messages to retrieve

        Returns:
            List of message dictionaries
        """
        key = self._get_key(conversation_id)

        if self.redis_client:
            try:
                # Get messages from Redis
                start = -limit if limit else 0
                messages_json = self.redis_client.lrange(key, start, -1)
                messages = [json.loads(msg) for msg in messages_json]
                logger.debug(f"Retrieved {len(messages)} messages for {conversation_id}")
                return messages
            except RedisError as e:
                logger.error(f"Redis error getting history: {e}")
                return []
        else:
            # Fallback to in-memory
            messages = self._memory_fallback.get(conversation_id, [])
            if limit:
                messages = messages[-limit:]
            return messages

    def get_context(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> str:
        """
        Get formatted conversation context for LLM

        Args:
            conversation_id: Unique conversation identifier
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted context string
        """
        history = self.get_history(conversation_id, limit=max_messages)

        if not history:
            return "No previous conversation context."

        context_lines = ["Previous conversation:"]
        for msg in history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_lines.append(f"{role}: {content}")

        return "\n".join(context_lines)

    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear conversation history

        Args:
            conversation_id: Unique conversation identifier
        """
        key = self._get_key(conversation_id)

        if self.redis_client:
            try:
                self.redis_client.delete(key)
                logger.info(f"Cleared conversation {conversation_id}")
            except RedisError as e:
                logger.error(f"Redis error clearing conversation: {e}")
        else:
            # Fallback to in-memory
            self._memory_fallback.pop(conversation_id, None)

    def get_all_conversations(self) -> List[str]:
        """
        Get list of all active conversation IDs

        Returns:
            List of conversation IDs
        """
        if self.redis_client:
            try:
                # Scan for all conversation keys
                keys = []
                cursor = 0
                while True:
                    cursor, partial_keys = self.redis_client.scan(
                        cursor, match="conversation:*", count=100
                    )
                    keys.extend(partial_keys)
                    if cursor == 0:
                        break
                # Extract conversation IDs from keys
                conversation_ids = [key.replace("conversation:", "") for key in keys]
                return conversation_ids
            except RedisError as e:
                logger.error(f"Redis error getting conversations: {e}")
                return []
        else:
            # Fallback to in-memory
            return list(self._memory_fallback.keys())

    def get_stats(self) -> Dict:
        """
        Get memory usage statistics

        Returns:
            Dictionary with memory stats
        """
        if self.redis_client:
            try:
                info = self.redis_client.info("memory")
                return {
                    "used_memory_human": info.get("used_memory_human", "N/A"),
                    "total_conversations": len(self.get_all_conversations()),
                    "backend": "redis"
                }
            except RedisError as e:
                logger.error(f"Redis error getting stats: {e}")
                return {"backend": "redis", "error": str(e)}
        else:
            # Fallback to in-memory
            total_messages = sum(len(msgs) for msgs in self._memory_fallback.values())
            return {
                "total_conversations": len(self._memory_fallback),
                "total_messages": total_messages,
                "backend": "in-memory (fallback)"
            }


# Singleton instance
_memory_instance: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """
    Get or create singleton ConversationMemory instance

    Returns:
        ConversationMemory instance
    """
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance
