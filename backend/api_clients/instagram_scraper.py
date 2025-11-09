import instaloader
import asyncio
from typing import Optional, Dict, Any, List
import logging
from api_clients.base import BaseAPIClient
from cache import cache_manager
from config import settings

logger = logging.getLogger(__name__)

class InstagramScraper(BaseAPIClient):
    def __init__(self):
        super().__init__("instagram_scraper", rate_limit=20)
        self.loader = None
        self.session_file = "instagram_session"
        
    async def _init_loader(self):
        if not self.loader:
            try:
                self.loader = instaloader.Instaloader(
                    download_videos=False,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False,
                    quiet=True
                )
                
                try:
                    self.loader.load_session_from_file("instagram", filename=self.session_file)
                except:
                    logger.info("No Instagram session found, using anonymous mode (limited features)")
            except Exception as e:
                logger.error(f"Error initializing Instaloader: {e}")
                self.loader = None
    
    async def search_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        await self._init_loader()
        if not self.loader:
            return None
        
        cache_key = f"instagram_scraper:username:{username}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            loop = asyncio.get_event_loop()
            profile = await loop.run_in_executor(
                None,
                lambda: instaloader.Profile.from_username(self.loader.context, username)
            )
            
            posts = []
            try:
                for post in profile.get_posts():
                    posts.append({
                        'shortcode': post.shortcode,
                        'url': f"https://www.instagram.com/p/{post.shortcode}/",
                        'caption': post.caption[:200] if post.caption else None,
                        'likes': post.likes,
                        'comments': post.comments,
                        'timestamp': post.date_utc.isoformat() if post.date_utc else None,
                        'is_video': post.is_video,
                        'thumbnail_url': post.url if not post.is_video else None
                    })
                    if len(posts) >= 12:
                        break
            except:
                pass
            
            result = {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'followees': profile.followees,
                'posts_count': profile.mediacount,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'profile_pic_url': profile.profile_pic_url,
                'external_url': profile.external_url,
                'posts': posts
            }
            
            await cache_manager.set(cache_key, result, self.cache_ttl)
            return result
        except Exception as e:
            logger.error(f"Instagram scraper error for {username}: {e}")
            return None
    
    async def search_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        await self._init_loader()
        if not self.loader:
            return None
        
        cache_key = f"instagram_scraper:name:{name}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            loop = asyncio.get_event_loop()
            profiles = await loop.run_in_executor(
                None,
                lambda: list(instaloader.TopSearchResults(self.loader.context, name).get_profiles())
            )
            
            results = []
            for profile in profiles[:10]:
                try:
                    result = {
                        'username': profile.username,
                        'full_name': profile.full_name,
                        'biography': profile.biography[:200] if profile.biography else None,
                        'followers': profile.followers,
                        'is_verified': profile.is_verified,
                        'is_private': profile.is_private,
                        'profile_pic_url': profile.profile_pic_url
                    }
                    results.append(result)
                except:
                    continue
            
            if results:
                result_data = {'profiles': results, 'count': len(results)}
                await cache_manager.set(cache_key, result_data, self.cache_ttl)
                return result_data
        except Exception as e:
            logger.error(f"Instagram name search error: {e}")
        
        return None
    
    async def search(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        if query_type == "username":
            return await self.search_by_username(query)
        elif query_type == "name":
            return await self.search_by_name(query)
        return None

