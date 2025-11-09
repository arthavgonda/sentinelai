from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class IPInfoClient(BaseAPIClient):
    def __init__(self):
        super().__init__("ipinfo", rate_limit=50000)
        self.api_token = settings.IPINFO_TOKEN
        self.base_url = "https://ipinfo.io"
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "ip":
            cache_key = f"ipinfo:ip:{query}"
            url = f"{self.base_url}/{query}"
            params = {"token": self.api_token}
            return await self._make_request("GET", url, cache_key, params=params)
        return None

