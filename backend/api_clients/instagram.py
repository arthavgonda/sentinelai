from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class InstagramClient(BaseAPIClient):
    def __init__(self):
        super().__init__("instagram", rate_limit=100)
        self.rapidapi_host = settings.INSTAGRAM_RAPIDAPI_HOST
        self.rapidapi_key = settings.INSTAGRAM_RAPIDAPI_KEY
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "username":
            cache_key = f"instagram:username:{query}"
            url = f"https://{self.rapidapi_host}/user/{query}"
            headers = {
                "X-RapidAPI-Host": self.rapidapi_host,
                "X-RapidAPI-Key": self.rapidapi_key
            }
            return await self._make_request("GET", url, cache_key, headers=headers)
        return None

