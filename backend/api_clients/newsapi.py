from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class NewsAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__("newsapi", rate_limit=100)
        self.api_key = settings.NEWSAPI_KEY
        self.base_url = "https://newsapi.org/v2"
        self.cache_ttl = settings.CACHE_TTL_NEWS
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type in ["name", "username", "email"]:
            cache_key = f"newsapi:{query_type}:{query}"
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "en"
            }
            return await self._make_request("GET", url, cache_key, params=params)
        return None

