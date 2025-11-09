from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class HunterClient(BaseAPIClient):
    def __init__(self):
        super().__init__("hunter", rate_limit=25)
        self.rapidapi_host = settings.HUNTER_RAPIDAPI_HOST
        self.rapidapi_key = settings.HUNTER_RAPIDAPI_KEY
        self.cache_ttl = settings.CACHE_TTL_EMAIL
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "email":
            cache_key = f"hunter:email:{query}"
            url = f"https://{self.rapidapi_host}/find_email"
            headers = {
                "X-RapidAPI-Host": self.rapidapi_host,
                "X-RapidAPI-Key": self.rapidapi_key
            }
            params = {"domain": query.split("@")[1] if "@" in query else query}
            return await self._make_request("GET", url, cache_key, headers=headers, params=params)
        elif query_type == "domain":
            cache_key = f"hunter:domain:{query}"
            url = f"https://{self.rapidapi_host}/domain_search"
            headers = {
                "X-RapidAPI-Host": self.rapidapi_host,
                "X-RapidAPI-Key": self.rapidapi_key
            }
            params = {"domain": query}
            return await self._make_request("GET", url, cache_key, headers=headers, params=params)
        return None

