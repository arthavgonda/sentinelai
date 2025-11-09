from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings
from cache import cache_manager
import asyncio
import logging

logger = logging.getLogger(__name__)

try:
    from telethon import TelegramClient
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Telethon not available, Telegram client disabled")

class TelegramClientWrapper(BaseAPIClient):
    def __init__(self):
        super().__init__("telegram", rate_limit=20)
        self.api_id = settings.API_ID_TELEGRAM
        self.api_hash = settings.API_KEY_TELEGRAM
        self.client = None
        self.available = TELEGRAM_AVAILABLE
        
    async def _init_client(self):
        if not self.client:
            try:
                self.client = TelegramClient('session', self.api_id, self.api_hash)
                await self.client.start()
            except Exception as e:
                logger.error(f"Telegram client init error: {e}")
                self.client = None
    
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if not self.available:
            return None
            
        await self._init_client()
        
        if not self.client:
            return None
        
        if query_type == "username":
            cache_key = f"telegram:username:{query}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
                
            try:
                entity = await self.client.get_entity(query)
                result = {
                    "username": entity.username,
                    "first_name": getattr(entity, "first_name", None),
                    "last_name": getattr(entity, "last_name", None),
                    "id": entity.id,
                    "phone": getattr(entity, "phone", None),
                    "verified": getattr(entity, "verified", False),
                    "bot": getattr(entity, "bot", False)
                }
                await cache_manager.set(cache_key, result, self.cache_ttl)
                return result
            except Exception as e:
                logger.error(f"Telegram search error: {e}")
        return None

