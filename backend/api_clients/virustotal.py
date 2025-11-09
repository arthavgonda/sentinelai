from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class VirusTotalClient(BaseAPIClient):
    def __init__(self):
        super().__init__("virustotal", rate_limit=4)
        self.api_key = settings.VIRUSTOTAL_API_KEY
        self.base_url = "https://www.virustotal.com/vtapi/v2"
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "email":
            cache_key = f"virustotal:email:{query}"
            url = f"{self.base_url}/domain/report"
            params = {
                "apikey": self.api_key,
                "domain": query.split("@")[1] if "@" in query else query
            }
            return await self._make_request("GET", url, cache_key, params=params)
        elif query_type == "username":
            cache_key = f"virustotal:url:{query}"
            url = f"{self.base_url}/url/report"
            params = {
                "apikey": self.api_key,
                "resource": query
            }
            return await self._make_request("GET", url, cache_key, params=params)
        return None

