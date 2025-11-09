import asyncio
from typing import Dict, List, Any, Optional
from collections import defaultdict
import time
import logging
from api_clients import (
    TwitterClient, InstagramClient, HunterClient, NumverifyClient,
    EtherscanClient, VirusTotalClient, NewsAPIClient, GoogleNewsClient,
    IPInfoClient, GitHubClient, TelegramClientWrapper, RedditClient
)
from api_clients.instagram_scraper import InstagramScraper
from services.correlation import CorrelationEngine
from services.web_scraper import web_scraper
from services.image_matcher import image_matcher
from services.google_search import google_search
from services.analysis_engine import analysis_engine
from services.google_vision import google_vision
from database import AsyncSessionLocal, Profile
from sqlalchemy import select
from cache import cache_manager
from utils.validators import validate_email, validate_phone, validate_username, normalize_email, normalize_phone, normalize_username, normalize_name, extract_domain, generate_username_variations, generate_name_variations

logger = logging.getLogger(__name__)

class APIOrchestrator:
    def __init__(self):
        self.clients = {
            "twitter": TwitterClient(),
            "instagram": InstagramClient(),
            "instagram_scraper": InstagramScraper(),
            "hunter": HunterClient(),
            "numverify": NumverifyClient(),
            "etherscan": EtherscanClient(),
            "virustotal": VirusTotalClient(),
            "newsapi": NewsAPIClient(),
            "googlenews": GoogleNewsClient(),
            "github": GitHubClient(),
            "telegram": TelegramClientWrapper(),
            "reddit": RedditClient()
        }
        self.correlation_engine = CorrelationEngine()
        self.priority_apis = ["twitter", "instagram_scraper", "hunter", "github", "newsapi", "googlenews"]
        self.secondary_apis = ["reddit", "virustotal", "etherscan"]
        self.background_apis = ["telegram", "numverify", "ipinfo", "instagram"]
        
    async def search(self, query: str, query_type: str, profile_id: Optional[int] = None, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        start_time = time.time()
        normalized_query = self._normalize_query(query, query_type)
        # Include Google search in total count
        total_apis = len(self.priority_apis) + len(self.secondary_apis) + len(self.background_apis) + 1  # +1 for Google search
        completed_count = 0
        
        cache_key = f"profile:{query_type}:{normalized_query}"
        cached_profile = await cache_manager.get(cache_key)
        if cached_profile:
            return cached_profile
        
        query_variations = self._generate_query_variations(normalized_query, query_type)
        
        if progress_callback:
            await progress_callback(5, "Preparing API queries...", 0, total_apis)
        
        priority_tasks = []
        priority_api_names = []
        secondary_tasks = []
        secondary_api_names = []
        background_tasks = []
        background_api_names = []
        
        # Add Google search as a task
        google_search_task = self._search_api("google_search", None, normalized_query, query_type, query_variations, progress_callback, completed_count, total_apis)
        priority_tasks.append(google_search_task)
        priority_api_names.append("google_search")
        
        for api_name, client in self.clients.items():
            task = self._search_api(api_name, client, normalized_query, query_type, query_variations, progress_callback, completed_count, total_apis)
            
            if api_name in self.priority_apis:
                priority_tasks.append(task)
                priority_api_names.append(api_name)
            elif api_name in self.secondary_apis:
                secondary_tasks.append(task)
                secondary_api_names.append(api_name)
            else:
                background_tasks.append(task)
                background_api_names.append(api_name)
        
        if progress_callback:
            await progress_callback(10, f"Querying {len(priority_api_names)} priority APIs...", 0, total_apis)
        
        results = {}
        completed_apis = set()
        
        try:
            priority_results = await asyncio.wait_for(
                asyncio.gather(*priority_tasks, return_exceptions=True),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.warning("Priority APIs timed out after 15 seconds")
            priority_results = [None] * len(priority_tasks)
        
        for i, api_name in enumerate(priority_api_names):
            if i < len(priority_results):
                if not isinstance(priority_results[i], Exception) and priority_results[i]:
                    results[api_name] = priority_results[i]
                    completed_apis.add(api_name)
                    completed_count += 1
                    if progress_callback:
                        progress = int((completed_count / total_apis) * 50)  # 50% for priority APIs
                        await progress_callback(progress, f"Completed {api_name}...", completed_count, total_apis)
                elif isinstance(priority_results[i], Exception):
                    logger.error(f"Priority API {api_name} error: {priority_results[i]}")
                    completed_count += 1
                else:
                    completed_count += 1
        
        initial_results = results.copy()
        
        try:
            secondary_results = await asyncio.wait_for(
                asyncio.gather(*secondary_tasks, return_exceptions=True),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            logger.warning("Secondary APIs timed out after 10 seconds")
            secondary_results = [None] * len(secondary_tasks)
        
        if progress_callback:
            await progress_callback(55, f"Querying {len(secondary_api_names)} secondary APIs...", completed_count, total_apis)
        
        for i, api_name in enumerate(secondary_api_names):
            if i < len(secondary_results):
                if not isinstance(secondary_results[i], Exception) and secondary_results[i]:
                    results[api_name] = secondary_results[i]
                    completed_apis.add(api_name)
                    completed_count += 1
                    if progress_callback:
                        progress = int((completed_count / total_apis) * 70)  # 70% for priority + secondary
                        await progress_callback(progress, f"Completed {api_name}...", completed_count, total_apis)
                elif isinstance(secondary_results[i], Exception):
                    logger.error(f"Secondary API {api_name} error: {secondary_results[i]}")
                    completed_count += 1
                else:
                    completed_count += 1
        
        if query_type in ["name", "username", "email"]:
            try:
                if progress_callback:
                    await progress_callback(75, "Searching blogs and articles...", completed_count, total_apis)
                blog_result = await asyncio.wait_for(
                    self._search_blogs(normalized_query, query_type),
                    timeout=25.0  # Increased timeout for blog scraping (allows time for multiple searches)
                )
                if blog_result and blog_result.get("blogs") and len(blog_result.get("blogs", [])) > 0:
                    results["web_scraper"] = blog_result
                    completed_apis.add("web_scraper")
                    completed_count += 1
                    blog_count = len(blog_result.get("blogs", []))
                    if progress_callback:
                        await progress_callback(80, f"Found {blog_count} articles", completed_count, total_apis)
            except asyncio.TimeoutError:
                logger.warning("Blog search timed out")
            except Exception as e:
                logger.error(f"Blog search error: {e}")
        
        background_future = asyncio.gather(*background_tasks, return_exceptions=True)
        
        # Extract and analyze images
        extracted_images = []
        image_matches = []
        try:
            if progress_callback:
                await progress_callback(85, "Extracting and analyzing images...", completed_count, total_apis)
            
            # Extract images from all sources
            extracted_images = await google_vision.extract_images_from_results(results)
            
            # Find image matches
            image_matches = await self._find_image_matches(results, normalized_query)
            
            if progress_callback:
                await progress_callback(90, "Image analysis complete", completed_count, total_apis)
        except Exception as e:
            logger.error(f"Image extraction/analysis error: {e}")
        
        if progress_callback:
            await progress_callback(95, "Correlating data...", completed_count, total_apis)
        correlation_result = self.correlation_engine.correlate_profiles(results)
        
        if progress_callback:
            await progress_callback(98, "Generating confidence report...", completed_count, total_apis)
        analysis_result = analysis_engine.analyze_profile(results, normalized_query, query_type)
        
        # Get primary image (most relevant photo)
        primary_image = None
        if extracted_images:
            # Prioritize knowledge panel images, then profile pictures
            for img in extracted_images:
                if img.get("source") == "knowledge_panel" or img.get("type") == "entity_image":
                    primary_image = img
                    break
            if not primary_image:
                primary_image = extracted_images[0]
        
        profile_data = {
            "query": normalized_query,
            "query_type": query_type,
            "results": results,
            "correlation": correlation_result,
            "analysis": analysis_result,
            "images": extracted_images,
            "primary_image": primary_image,
            "image_matches": image_matches if image_matches else [],
            "completed_apis": list(completed_apis),
            "pending_apis": [api for api in self.background_apis if api not in completed_apis],
            "collection_time": time.time() - start_time,
            "status": "partial" if background_tasks else "complete"
        }
        
        await cache_manager.set(cache_key, profile_data, 3600)
        
        if profile_id:
            await self._save_profile(profile_id, profile_data)
        
        asyncio.create_task(self._complete_background_tasks(background_future, background_api_names, profile_data, cache_key))
        
        return profile_data
    
    async def _search_api(self, api_name: str, client: Any, query: str, query_type: str, variations: List[str], progress_callback: Optional[callable] = None, completed_count: int = 0, total_apis: int = 0) -> Optional[Dict[str, Any]]:
        try:
            # Handle Google search separately
            if api_name == "google_search":
                if progress_callback:
                    await progress_callback(60, "Searching Google...", completed_count, total_apis)
                result = await google_search.search(query, max_results=10)
                return result
            
            if client is None:
                logger.warning(f"Client {api_name} is None, skipping")
                return None
            
            # Add timeout to individual API calls
            search_query = query
            search_type = query_type
            
            if query_type == "name":
                if api_name in ["newsapi", "googlenews", "reddit"]:
                    search_type = "name"
                    result = await asyncio.wait_for(client.search(search_query, search_type), timeout=5.0)
                    if result:
                        return result
                elif api_name in ["twitter", "instagram_scraper"]:
                    search_type = "name"
                    result = await asyncio.wait_for(client.search(search_query, search_type), timeout=5.0)
                    if result:
                        return result
                elif api_name in ["instagram", "github"]:
                    for variation in variations[:5]:
                        search_type = "username"
                        try:
                            result = await asyncio.wait_for(client.search(variation, search_type), timeout=5.0)
                            if result:
                                return result
                        except asyncio.TimeoutError:
                            continue
                else:
                    for variation in variations[:3]:
                        search_type = "username"
                        try:
                            result = await asyncio.wait_for(client.search(variation, search_type), timeout=5.0)
                            if result:
                                return result
                        except asyncio.TimeoutError:
                            continue
            else:
                try:
                    result = await asyncio.wait_for(client.search(search_query, search_type), timeout=5.0)
                    if result:
                        return result
                except asyncio.TimeoutError:
                    pass
                
                for variation in variations[:3]:
                    try:
                        result = await asyncio.wait_for(client.search(variation, search_type), timeout=5.0)
                        if result:
                            return result
                    except asyncio.TimeoutError:
                        continue
        except asyncio.TimeoutError:
            logger.warning(f"API {api_name} timed out")
        except Exception as e:
            logger.error(f"API {api_name} error: {e}")
        return None
    
    async def _search_blogs(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """Search blogs and articles using web scraper"""
        try:
            if query_type in ["name", "username", "email"]:
                # web_scraper.search_blogs now returns a Dict with "blogs" key
                result = await web_scraper.search_blogs(query, max_results=10)
                if result and result.get("blogs") and len(result.get("blogs", [])) > 0:
                    return result
        except Exception as e:
            logger.error(f"Blog search error: {e}")
        return None
    
    async def _find_image_matches(self, results: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        try:
            query_images = []
            
            for api_name, data in results.items():
                if not data or not isinstance(data, dict):
                    continue
                
                if api_name == "instagram_scraper":
                    if data.get('profile_pic_url'):
                        query_images.append(data['profile_pic_url'])
                    if data.get('posts'):
                        for post in data['posts'][:3]:
                            if post.get('thumbnail_url'):
                                query_images.append(post['thumbnail_url'])
                    if data.get('profiles'):
                        for profile in data['profiles'][:2]:
                            if profile.get('profile_pic_url'):
                                query_images.append(profile['profile_pic_url'])
                
                elif api_name == "twitter":
                    if data.get('profile_image'):
                        query_images.append(data['profile_image'])
                    if data.get('users'):
                        for user in data['users'][:3]:
                            if user.get('profile_image'):
                                query_images.append(user['profile_image'])
                
                elif api_name == "github":
                    user = data.get('user', {})
                    if user and user.get('avatar_url'):
                        query_images.append(user['avatar_url'])
                
                elif api_name == "instagram":
                    if data.get('profile_pic_url') or data.get('profile_picture'):
                        query_images.append(data.get('profile_pic_url') or data.get('profile_picture'))
            
            if not query_images:
                return []
            
            candidate_images = []
            
            for api_name, data in results.items():
                if not data or not isinstance(data, dict):
                    continue
                
                if api_name == "web_scraper":
                    blogs = data.get('blogs', [])
                    for blog in blogs:
                        images = blog.get('images', [])
                        for img in images:
                            img_url = img.get('url') if isinstance(img, dict) else img
                            if img_url:
                                candidate_images.append({
                                    'url': img_url,
                                    'source': blog.get('url'),
                                    'title': blog.get('title'),
                                    'context': blog.get('content', '')[:200] if blog.get('content') else ''
                                })
                
                elif api_name in ["newsapi", "googlenews"]:
                    articles = data.get('articles', []) or data.get('items', []) or []
                    for article in articles[:15]:
                        if isinstance(article, dict):
                            img_url = article.get('urlToImage') or article.get('image') or article.get('url')
                            if img_url and img_url.startswith('http'):
                                candidate_images.append({
                                    'url': img_url,
                                    'source': article.get('url') or article.get('link'),
                                    'title': article.get('title'),
                                    'context': (article.get('description') or article.get('summary') or '')[:200]
                                })
            
            if candidate_images and query_images:
                matches = await image_matcher.find_matching_images(query_images, candidate_images)
                return matches[:10]
        
        except Exception as e:
            logger.error(f"Image matching error: {e}")
        
        return []
    
    def _normalize_query(self, query: str, query_type: str) -> str:
        if query_type == "email":
            return normalize_email(query)
        elif query_type == "phone":
            return normalize_phone(query)
        elif query_type == "username":
            return normalize_username(query)
        elif query_type == "name":
            return normalize_name(query)
        return query.strip()
    
    def _generate_query_variations(self, query: str, query_type: str) -> List[str]:
        variations = [query]
        
        if query_type == "email":
            domain = extract_domain(query)
            if domain:
                variations.append(domain)
            local_part = query.split("@")[0] if "@" in query else ""
            if local_part:
                variations.extend(generate_username_variations(local_part))
        elif query_type == "username":
            variations.extend(generate_username_variations(query))
        elif query_type == "name":
            variations.extend(generate_name_variations(query))
        
        return list(set(variations))
    
    async def _save_profile(self, profile_id: int, profile_data: Dict[str, Any]):
        try:
            db = AsyncSessionLocal()
            try:
                result = await db.execute(select(Profile).where(Profile.id == profile_id))
                profile = result.scalar_one_or_none()
                if profile:
                    profile.data = profile_data
                    profile.status = profile_data.get("status", "complete")
                    if profile_data.get("correlation") and profile_data["correlation"].get("confidence_scores"):
                        scores = profile_data["correlation"]["confidence_scores"]
                        profile.correlation_score = sum(scores.values()) / len(scores) if scores else 0.0
                    await db.commit()
            finally:
                await db.close()
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
    
    async def _complete_background_tasks(self, background_future, background_api_names: List[str], profile_data: Dict[str, Any], cache_key: str):
        try:
            background_results = await background_future
            for i, api_name in enumerate(background_api_names):
                if i < len(background_results) and not isinstance(background_results[i], Exception) and background_results[i]:
                    profile_data["results"][api_name] = background_results[i]
                    if api_name not in profile_data["completed_apis"]:
                        profile_data["completed_apis"].append(api_name)
            
            if profile_data["pending_apis"]:
                profile_data["pending_apis"] = [
                    api for api in profile_data["pending_apis"]
                    if api not in profile_data["completed_apis"]
                ]
            
            updated_image_matches = await self._find_image_matches(profile_data["results"], profile_data["query"])
            if updated_image_matches:
                profile_data["image_matches"] = updated_image_matches
            
            profile_data["status"] = "complete"
            profile_data["correlation"] = self.correlation_engine.correlate_profiles(profile_data["results"])
            
            await cache_manager.set(cache_key, profile_data, 3600)
        except Exception as e:
            logger.error(f"Error completing background tasks: {e}")
    
    async def close(self):
        for client in self.clients.values():
            try:
                await client.close()
            except:
                pass

orchestrator = APIOrchestrator()

