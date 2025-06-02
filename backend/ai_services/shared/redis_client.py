# Redis client for caching
import redis
import json
import asyncio
from typing import Any, Optional, List, Dict
from .config import settings
import hashlib

class RedisClient:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.async_redis = None
    
    async def get_async_client(self):
        """Get async Redis client"""
        if self.async_redis is None:
            import redis.asyncio as aioredis
            self.async_redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        return self.async_redis
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in Redis with optional TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    async def get_async(self, key: str) -> Optional[Any]:
        """Async get value from Redis"""
        try:
            client = await self.get_async_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis ASYNC GET error: {e}")
            return None
    
    async def set_async(self, key: str, value: Any, ttl: int = None) -> bool:
        """Async set value in Redis with optional TTL"""
        try:
            client = await self.get_async_client()
            serialized_value = json.dumps(value, default=str)
            if ttl:
                return await client.setex(key, ttl, serialized_value)
            else:
                return await client.set(key, serialized_value)
        except Exception as e:
            print(f"Redis ASYNC SET error: {e}")
            return False
    
    def cache_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding with text hash as key"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        return self.set(key, embedding, settings.embedding_cache_ttl)
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding by text hash"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        return self.get(key)
    
    async def cache_embedding_async(self, text: str, embedding: List[float]) -> bool:
        """Async cache embedding with text hash as key"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        return await self.set_async(key, embedding, settings.embedding_cache_ttl)
    
    async def get_cached_embedding_async(self, text: str) -> Optional[List[float]]:
        """Async get cached embedding by text hash"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        key = f"embedding:{text_hash}"
        return await self.get_async(key)
    
    def cache_search_results(self, query: str, results: List[Dict]) -> bool:
        """Cache search results"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"search:{query_hash}"
        return self.set(key, results, settings.cache_ttl)
    
    def get_cached_search_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"search:{query_hash}"
        return self.get(key)
    
    def increment_rate_limit(self, identifier: str) -> int:
        """Increment rate limit counter"""
        key = f"rate_limit:{identifier}"
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, settings.rate_limit_period)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            print(f"Rate limit error: {e}")
            return 0
    
    def get_rate_limit(self, identifier: str) -> int:
        """Get current rate limit count"""
        key = f"rate_limit:{identifier}"
        try:
            count = self.redis_client.get(key)
            return int(count) if count else 0
        except Exception as e:
            print(f"Get rate limit error: {e}")
            return 0

# Global Redis client instance
redis_client = RedisClient()