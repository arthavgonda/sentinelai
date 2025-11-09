from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings
import feedparser
import asyncio
import logging

logger = logging.getLogger(__name__)

class GoogleNewsClient(BaseAPIClient):
    def __init__(self):
        super().__init__("googlenews", rate_limit=100)
        self.api_key = settings.GOOGLE_NEWS_API_KEY
        self.cache_ttl = settings.CACHE_TTL_NEWS
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type in ["name", "username", "email"]:
            from urllib.parse import quote_plus
            cache_key = f"googlenews:{query_type}:{query}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
                
            try:
                encoded_query = quote_plus(query)
                url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(None, lambda: feedparser.parse(url))
                
                articles = []
                for entry in feed.entries[:20]:
                    articles.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", "")
                    })
                
                result = {"articles": articles, "total": len(articles)}
                await cache_manager.set(cache_key, result, self.cache_ttl)
                return result
            except Exception as e:
                logger.error(f"Google News search error: {e}")
        return None

