import redis.asyncio as redis
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
                socket_connect_timeout=2
            )
            await self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self.redis_client = None
        
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            
    def _generate_key(self, prefix: str, *args) -> str:
        key_str = ":".join(str(arg) for arg in args)
        normalized = key_str.lower().strip()
        return f"{prefix}:{normalized}"
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            try:
                await self.connect()
            except:
                return None
        if not self.redis_client:
            return None
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        if not self.redis_client:
            await self.connect()
        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        if not self.redis_client:
            await self.connect()
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def get_or_set(self, key: str, fetch_func, ttl: int = 3600) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await fetch_func()
        if value is not None:
            await self.set(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str):
        if not self.redis_client:
            await self.connect()
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
    
    async def increment(self, key: str, amount: int = 1) -> int:
        if not self.redis_client:
            await self.connect()
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0
    
    async def set_hash(self, key: str, field: str, value: Any):
        if not self.redis_client:
            await self.connect()
        try:
            await self.redis_client.hset(key, field, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Cache hash set error: {e}")
    
    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        if not self.redis_client:
            await self.connect()
        try:
            data = await self.redis_client.hget(key, field)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache hash get error: {e}")
        return None
    
    async def get_all_hash(self, key: str) -> Dict[str, Any]:
        if not self.redis_client:
            await self.connect()
        try:
            data = await self.redis_client.hgetall(key)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Cache hash get all error: {e}")
            return {}

cache_manager = CacheManager()

