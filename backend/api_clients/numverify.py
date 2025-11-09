from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings
from utils.validators import normalize_phone

class NumverifyClient(BaseAPIClient):
    def __init__(self):
        super().__init__("numverify", rate_limit=1000)
        self.api_key = settings.NUMVERIFY_API_KEY
        self.cache_ttl = 2592000
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "phone":
            normalized = normalize_phone(query)
            cache_key = f"numverify:phone:{normalized}"
            url = f"http://apilayer.net/api/validate"
            params = {
                "access_key": self.api_key,
                "number": normalized,
                "country_code": "",
                "format": 1
            }
            return await self._make_request("GET", url, cache_key, params=params)
        return None

