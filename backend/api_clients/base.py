import httpx
import asyncio
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from config import settings
from cache import cache_manager
from utils.circuit_breaker import circuit_breaker_manager
from utils.rate_limiter import rate_limiter_manager
import logging
import time

logger = logging.getLogger(__name__)

class BaseAPIClient(ABC):
    def __init__(self, api_name: str, rate_limit: int = 60):
        self.api_name = api_name
        self.rate_limiter = rate_limiter_manager.get_limiter(api_name, rate_limit)
        self.circuit_breaker = circuit_breaker_manager.get_breaker(api_name)
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT, limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))
        self.cache_ttl = settings.CACHE_TTL_SOCIAL
        
    async def _make_request(self, method: str, url: str, cache_key: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        if cache_key:
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                return cached
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            response = await self.circuit_breaker.call(
                self.client.request,
                method=method,
                url=url,
                **kwargs
            )
            
            if response.status_code == 200:
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw": response.text}
                
                if cache_key:
                    await cache_manager.set(cache_key, data, self.cache_ttl)
                
                return data
            else:
                logger.warning(f"{self.api_name} API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"{self.api_name} API exception: {e}")
            return None
    
    @abstractmethod
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        pass
    
    async def close(self):
        await self.client.aclose()

