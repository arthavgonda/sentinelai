import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import re
from services.image_matcher import image_matcher

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    async def scrape_blog(self, url: str, query: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    title = soup.find('title')
                    title_text = title.get_text() if title else ""
                    
                    # Extract main content
                    # Try to find article or main content area first
                    article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'article|content|post|entry', re.I))
                    if article:
                        content = article.find_all(['p', 'div', 'span'])
                    else:
                        content = soup.find_all(['p', 'article', 'div'])
                    
                    text_content = ' '.join([p.get_text().strip() for p in content[:30] if p.get_text().strip()])
                    
                    # More lenient matching - check if any query words appear
                    query_lower = query.lower()
                    query_words = set(query_lower.split())
                    title_lower = title_text.lower()
                    content_lower = text_content.lower()
                    
                    # Check if at least 50% of query words appear
                    title_matches = sum(1 for word in query_words if word in title_lower)
                    content_matches = sum(1 for word in query_words if word in content_lower)
                    
                    if title_matches < len(query_words) * 0.3 and content_matches < len(query_words) * 0.3:
                        return None
                    
                    images = image_matcher.extract_images_from_html(html, url)
                    
                    return {
                        'url': url,
                        'title': title_text,
                        'description': text_content[:300],  # Short description
                        'content': text_content,  # Full content for analysis
                        'images': images,
                        'matches': self._find_matches(text_content, query),
                        'source': 'blog'
                    }
        except Exception as e:
            logger.error(f"Error scraping blog {url}: {e}")
            return None
    
    async def search_blogs(self, query: str, max_results: int = 10) -> Dict:
        from urllib.parse import quote_plus
        encoded_query = quote_plus(query)
        
        search_queries = [
            f"{query} blog",
            f"{query} article",
            f'"{query}"',
            f"{query} news",
            f"{query} biography",
            f"{query} profile"
        ]
        
        results = []
        seen_urls = set()
        
        for search_query in search_queries[:3]:  # Try 3 different search queries
            try:
                encoded = quote_plus(search_query)
                search_url = f"https://www.google.com/search?q={encoded}&num=10"
                blog_urls = await self._get_google_results(search_url, max_results=8)
                
                for url in blog_urls:
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    blog_data = await self.scrape_blog(url, query)
                    if blog_data:
                        results.append(blog_data)
                    if len(results) >= max_results:
                        break
                
                if len(results) >= max_results:
                    break
            except Exception as e:
                logger.error(f"Error searching blogs: {e}")
        
        return {
            "blogs": results,
            "count": len(results),
            "query": query
        }
    
    async def _get_google_results(self, search_url: str, max_results: int = 5) -> List[str]:
        urls = []
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        return urls
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        if not href:
                            continue
                        
                        if href.startswith('/url?q='):
                            href = href.split('/url?q=')[1].split('&')[0]
                        
                        if href and href.startswith('http') and 'google.com' not in href and 'webcache' not in href:
                            try:
                                from urllib.parse import unquote
                                href = unquote(href)
                                if href not in urls:
                                    urls.append(href)
                                    if len(urls) >= max_results:
                                        break
                            except:
                                continue
        except Exception as e:
            logger.error(f"Error getting Google results: {e}")
        
        return urls
    
    def _find_matches(self, text: str, query: str) -> List[str]:
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        words = query_lower.split()
        for word in words:
            if word in text_lower:
                start = text_lower.find(word)
                context = text[max(0, start-50):start+len(word)+50]
                matches.append(context.strip())
        
        return matches[:3]
    
    async def extract_images_from_url(self, url: str) -> List[Dict]:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    images = image_matcher.extract_images_from_html(html, url)
                    return images
        except Exception as e:
            logger.error(f"Error extracting images from {url}: {e}")
            return []

web_scraper = WebScraper()

