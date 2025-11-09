import asyncio
import time
from typing import Dict, Optional
from collections import deque
from config import settings
import logging

logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
        
    async def acquire(self, tokens: int = 1) -> bool:
        async with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    async def wait_for_token(self, tokens: int = 1, timeout: float = 30.0):
        start = time.time()
        while time.time() - start < timeout:
            if await self.acquire(tokens):
                return True
            await asyncio.sleep(0.1)
        return False

class RateLimiter:
    def __init__(self, name: str, requests_per_minute: int):
        self.name = name
        self.requests_per_minute = requests_per_minute
        self.bucket = TokenBucket(requests_per_minute, requests_per_minute / 60.0)
        self.request_times = deque(maxlen=requests_per_minute)
        self.lock = asyncio.Lock()
        
    async def acquire(self) -> bool:
        async with self.lock:
            now = time.time()
            self.request_times.append(now)
            
            if len(self.request_times) < self.requests_per_minute:
                return await self.bucket.acquire()
            
            oldest_request = self.request_times[0]
            time_elapsed = now - oldest_request
            
            if time_elapsed < 60.0:
                wait_time = 60.0 - time_elapsed
                await asyncio.sleep(wait_time)
                return await self.bucket.acquire()
            
            return await self.bucket.acquire()
    
    async def wait_if_needed(self):
        if not await self.acquire():
            await self.bucket.wait_for_token()

class RateLimiterManager:
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        
    def get_limiter(self, name: str, requests_per_minute: int = 60) -> RateLimiter:
        if name not in self.limiters:
            self.limiters[name] = RateLimiter(name, requests_per_minute)
        return self.limiters[name]

rate_limiter_manager = RateLimiterManager()

