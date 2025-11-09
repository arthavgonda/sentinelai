from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class EtherscanClient(BaseAPIClient):
    def __init__(self):
        super().__init__("etherscan", rate_limit=5)
        self.api_key = settings.ETHERSCAN_API_KEY
        self.base_url = "https://api.etherscan.io/api"
        self.cache_ttl = settings.CACHE_TTL_BLOCKCHAIN
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type in ["email", "username"]:
            cache_key = f"etherscan:ens:{query}"
            params = {
                "module": "proxy",
                "action": "eth_getEnsName",
                "apikey": self.api_key,
                "address": query
            }
            ens_result = await self._make_request("GET", self.base_url, cache_key, params=params)
            
            if query_type == "email" and "@" in query:
                domain = query.split("@")[1]
                cache_key_domain = f"etherscan:domain:{domain}"
                params_domain = {
                    "module": "proxy",
                    "action": "eth_getEnsName",
                    "apikey": self.api_key
                }
                domain_result = await self._make_request("GET", self.base_url, cache_key_domain, params=params_domain)
                return {"ens": ens_result, "domain": domain_result} if ens_result or domain_result else None
            
            return ens_result
        return None

