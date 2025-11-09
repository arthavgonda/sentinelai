from api_clients.base import BaseAPIClient
from typing import Optional, Dict, Any
from cache import cache_manager
import praw
import asyncio
import logging

logger = logging.getLogger(__name__)

class RedditClient(BaseAPIClient):
    def __init__(self):
        super().__init__("reddit", rate_limit=60)
        from config import settings
        try:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
        except Exception as e:
            logger.error(f"Reddit client initialization error: {e}")
            self.reddit = None
        
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if not self.reddit:
            return None
            
        if query_type == "username":
            cache_key = f"reddit:username:{query}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
                
            try:
                loop = asyncio.get_event_loop()
                redditor = await loop.run_in_executor(
                    None,
                    lambda: self.reddit.redditor(query)
                )
                
                submissions = await loop.run_in_executor(
                    None,
                    lambda: list(redditor.submissions.new(limit=10))
                )
                
                comments = await loop.run_in_executor(
                    None,
                    lambda: list(redditor.comments.new(limit=10))
                )
                
                result = {
                    "username": redditor.name,
                    "created_utc": redditor.created_utc,
                    "comment_karma": redditor.comment_karma,
                    "link_karma": redditor.link_karma,
                    "submissions": [{"title": s.title, "score": s.score, "created_utc": s.created_utc, "url": f"https://reddit.com{s.permalink}"} for s in submissions],
                    "comments": [{"body": c.body[:200], "score": c.score, "created_utc": c.created_utc, "subreddit": c.subreddit.display_name} for c in comments]
                }
                
                await cache_manager.set(cache_key, result, self.cache_ttl)
                return result
            except Exception as e:
                logger.error(f"Reddit search error: {e}")
        elif query_type == "name":
            cache_key = f"reddit:name:{query}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
                
            try:
                loop = asyncio.get_event_loop()
                search_query = query.replace(" ", " OR ")
                subreddits = await loop.run_in_executor(
                    None,
                    lambda: list(self.reddit.subreddits.search(query, limit=10))
                )
                
                posts = await loop.run_in_executor(
                    None,
                    lambda: list(self.reddit.subreddit("all").search(query, limit=20, sort="relevance"))
                )
                
                result = {
                    "search_query": query,
                    "subreddits_found": [{"name": s.display_name, "subscribers": s.subscribers} for s in subreddits[:5]],
                    "posts_found": [{"title": p.title, "score": p.score, "subreddit": p.subreddit.display_name, "url": f"https://reddit.com{p.permalink}", "created_utc": p.created_utc} for p in posts[:10]]
                }
                
                await cache_manager.set(cache_key, result, self.cache_ttl)
                return result
            except Exception as e:
                logger.error(f"Reddit name search error: {e}")
        return None

