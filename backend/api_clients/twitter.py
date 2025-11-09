from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from config import settings
import tweepy
import asyncio
import logging

logger = logging.getLogger(__name__)

class TwitterClient(BaseAPIClient):
    def __init__(self):
        super().__init__("twitter", rate_limit=300)
        self.api_key = settings.API_KEY_X
        self.api_secret = settings.API_KEY_SECRET_X
        self.client_v2 = None
        
    async def _init_client(self):
        if not self.client_v2:
            client = tweepy.Client(
                bearer_token=self.api_key,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                wait_on_rate_limit=True
            )
            self.client_v2 = client
    
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        await self._init_client()
        
        if query_type == "email":
            cache_key = f"twitter:email:{query}"
            return await self._search_by_email(query, cache_key)
        elif query_type == "username":
            cache_key = f"twitter:username:{query}"
            return await self._search_by_username(query, cache_key)
        elif query_type == "name":
            cache_key = f"twitter:name:{query}"
            return await self._search_by_name(query, cache_key)
        elif query_type == "phone":
            return None
        return None
    
    async def _search_by_username(self, username: str, cache_key: str) -> Optional[Dict[str, Any]]:
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
            
        try:
            loop = asyncio.get_event_loop()
            user = await loop.run_in_executor(
                None,
                lambda: self.client_v2.get_user(username=username, user_fields=["description", "public_metrics", "created_at", "location", "profile_image_url"])
            )
            
            if user.data:
                tweets = await loop.run_in_executor(
                    None,
                    lambda: self.client_v2.get_users_tweets(id=user.data.id, max_results=10, tweet_fields=["created_at", "public_metrics"])
                )
                
                result = {
                    "username": user.data.username,
                    "name": user.data.name,
                    "description": user.data.description,
                    "followers": user.data.public_metrics.get("followers_count", 0) if hasattr(user.data, "public_metrics") else 0,
                    "following": user.data.public_metrics.get("following_count", 0) if hasattr(user.data, "public_metrics") else 0,
                    "tweets": user.data.public_metrics.get("tweet_count", 0) if hasattr(user.data, "public_metrics") else 0,
                    "created_at": str(user.data.created_at) if hasattr(user.data, "created_at") else None,
                    "location": user.data.location if hasattr(user.data, "location") else None,
                    "profile_image": user.data.profile_image_url if hasattr(user.data, "profile_image_url") else None,
                    "recent_tweets": [{"text": t.text, "created_at": str(t.created_at), "likes": t.public_metrics.get("like_count", 0) if hasattr(t, "public_metrics") else 0} for t in (tweets.data or [])] if tweets.data else []
                }
                
                await cache_manager.set(cache_key, result, self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
        return None
    
    async def _search_by_email(self, email: str, cache_key: str) -> Optional[Dict[str, Any]]:
        return None
    
    async def _search_by_name(self, name: str, cache_key: str) -> Optional[Dict[str, Any]]:
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
            
        try:
            loop = asyncio.get_event_loop()
            try:
                users = await loop.run_in_executor(
                    None,
                    lambda: self.client_v2.search_users(query=name, max_results=10, user_fields=["description", "public_metrics", "created_at", "location", "profile_image_url"])
                )
            except Exception as search_error:
                logger.warning(f"Twitter search_users failed, trying alternative: {search_error}")
                return None
            
            if users and hasattr(users, 'data') and users.data:
                results = []
                for user in users.data[:5]:
                    try:
                        result = {
                            "username": getattr(user, "username", None),
                            "name": getattr(user, "name", None),
                            "description": getattr(user, "description", None),
                            "followers": user.public_metrics.get("followers_count", 0) if hasattr(user, "public_metrics") and user.public_metrics else 0,
                            "following": user.public_metrics.get("following_count", 0) if hasattr(user, "public_metrics") and user.public_metrics else 0,
                            "location": getattr(user, "location", None),
                            "profile_image": getattr(user, "profile_image_url", None),
                        }
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Error processing Twitter user: {e}")
                        continue
                
                if results:
                    result_data = {"users": results, "count": len(results)}
                    await cache_manager.set(cache_key, result_data, self.cache_ttl)
                    return result_data
        except Exception as e:
            logger.error(f"Twitter name search error: {e}")
        return None

