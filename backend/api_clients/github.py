from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings

class GitHubClient(BaseAPIClient):
    def __init__(self):
        super().__init__("github", rate_limit=5000)
        self.api_token = settings.GITHUB_API_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "username":
            cache_key = f"github:username:{query}"
            user_url = f"{self.base_url}/users/{query}"
            repos_url = f"{self.base_url}/users/{query}/repos"
            
            user_data = await self._make_request("GET", user_url, f"{cache_key}:user", headers=self.headers)
            repos_data = await self._make_request("GET", repos_url, f"{cache_key}:repos", headers=self.headers, params={"per_page": 10, "sort": "updated"})
            
            if user_data:
                return {
                    "user": user_data,
                    "repos": repos_data if repos_data else []
                }
        elif query_type == "email":
            cache_key = f"github:email:{query}"
            url = f"{self.base_url}/search/users"
            params = {"q": f"{query} in:email"}
            result = await self._make_request("GET", url, cache_key, headers=self.headers, params=params)
            return result
        return None

