import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import quote_plus, urlencode
import re

logger = logging.getLogger(__name__)

class GoogleSearch:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    async def search(self, query: str, max_results: int = 10) -> Dict[str, any]:
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        logger.warning(f"Google search returned status {response.status}")
                        return {"results": [], "ai_summary": None, "total": 0}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract AI Summary / Overview (Google's AI-generated summary)
                    ai_summary = self._extract_ai_summary(soup)
                    
                    # Extract regular search results
                    results = self._extract_search_results(soup, query)
                    
                    # Extract knowledge panel
                    knowledge_panel = self._extract_knowledge_panel(soup)
                    
                    # Extract images from knowledge panel
                    images = self._extract_images(soup)
                    
                    # Extract people also ask
                    people_also_ask = self._extract_people_also_ask(soup)
                    
                    # Extract description from knowledge panel or AI summary
                    description = None
                    if knowledge_panel and knowledge_panel.get("description"):
                        description = knowledge_panel.get("description")
                    elif ai_summary and ai_summary.get("text"):
                        description = ai_summary.get("text")
                    
                    return {
                        "results": results[:max_results],
                        "ai_summary": ai_summary,
                        "knowledge_panel": knowledge_panel,
                        "description": description,  # Main description for display
                        "images": images,
                        "people_also_ask": people_also_ask,
                        "total": len(results)
                    }
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {"results": [], "ai_summary": None, "total": 0}
    
    def _extract_ai_summary(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract AI-generated summary from Google (AI Overview)"""
        try:
            # Try multiple selectors for AI Overview / Generated Summary
            selectors = [
                ('div', {'class': re.compile(r'ai.*overview|generated.*summary|ai.*summary', re.I)}),
                ('div', {'id': re.compile(r'overview|summary|ai.*answer', re.I)}),
                ('div', {'data-ved': True}),
                ('div', {'class': re.compile(r'featured|snippet|answer.*box', re.I)}),
            ]
            
            for tag, attrs in selectors:
                elements = soup.find_all(tag, attrs)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    # Check if it looks like an AI summary (substantial text, multiple sentences)
                    if len(text) > 150 and text.count('.') >= 2:
                        # Check for AI-like indicators
                        if any(indicator in text.lower() for indicator in ['according to', 'sources', 'research', 'studies', 'based on']):
                            return {
                                "text": text[:800],
                                "source": "Google AI Overview",
                                "type": "ai_summary"
                            }
            
            # Look for featured snippets (Google's answer boxes)
            featured_selectors = [
                soup.find('div', class_=re.compile(r'Z0LcW|hgKElc|XcVN5d', re.I)),  # Google's answer box classes
                soup.find('span', class_=re.compile(r'hgKElc|Z0LcW', re.I)),
                soup.find('div', id=re.compile(r'kp-wp-tab-overview', re.I)),
            ]
            
            for featured in featured_selectors:
                if featured:
                    text = featured.get_text(strip=True)
                    if len(text) > 50:
                        return {
                            "text": text[:800],
                            "source": "Google Featured Snippet",
                            "type": "featured_snippet"
                        }
            
            # Look for knowledge graph summary
            knowledge_summary = soup.find('div', class_=re.compile(r'kno.*desc|kno.*about', re.I))
            if knowledge_summary:
                text = knowledge_summary.get_text(strip=True)
                if len(text) > 100:
                    return {
                        "text": text[:800],
                        "source": "Google Knowledge Graph",
                        "type": "knowledge_summary"
                    }
        except Exception as e:
            logger.error(f"Error extracting AI summary: {e}")
        return None
    
    def _extract_search_results(self, soup: BeautifulSoup, query: str) -> List[Dict[str, str]]:
        results = []
        try:
            # Find search result containers - Google uses 'g' class for results
            result_divs = soup.find_all('div', class_='g')
            if not result_divs:
                # Try alternative selectors
                result_divs = soup.find_all('div', class_=re.compile(r'result|search.*result', re.I))
            
            for div in result_divs[:15]:  # Limit to first 15 results
                try:
                    # Extract title (h3 is standard for Google results)
                    title_elem = div.find('h3')
                    if not title_elem:
                        title_elem = div.find('a', href=True)
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Extract URL
                    link_elem = div.find('a', href=True)
                    url = None
                    if link_elem:
                        url = link_elem.get('href', '')
                        # Handle Google's URL redirect format
                        if url.startswith('/url?'):
                            url_match = re.search(r'[?&]q=([^&]+)', url)
                            if url_match:
                                from urllib.parse import unquote
                                url = unquote(url_match.group(1))
                        elif url.startswith('/'):
                            continue  # Skip internal Google links
                    
                    # Extract snippet/description
                    snippet_elem = div.find('span', class_=re.compile(r'aCOpRe|st', re.I)) or \
                                  div.find('div', class_=re.compile(r'VwiC3b|IsZvec', re.I)) or \
                                  div.find('span', class_=re.compile(r'snippet', re.I))
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else None
                    
                    if title and url and url.startswith('http') and len(title) > 5:
                        results.append({
                            "title": title[:200],
                            "url": url,
                            "snippet": (snippet or "")[:300],
                            "query_match": query.lower() in (title or "").lower() or query.lower() in (snippet or "").lower()
                        })
                except Exception as e:
                    logger.debug(f"Error parsing search result: {e}")
                    continue
            
            # Remove duplicates
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            
            return unique_results
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
        
        return results
    
    def _extract_knowledge_panel(self, soup: BeautifulSoup) -> Optional[Dict[str, any]]:
        """Extract knowledge panel information"""
        try:
            # Try multiple selectors for knowledge panel
            knowledge_panel = soup.find('div', class_=re.compile(r'knowledge|kp|info.*box|kno.*card', re.I))
            if not knowledge_panel:
                knowledge_panel = soup.find('div', id=re.compile(r'kp-wp|knowledge', re.I))
            
            if knowledge_panel:
                data = {}
                description = None
                
                # Extract description text
                desc_elem = knowledge_panel.find('div', class_=re.compile(r'kno.*desc|about|bio', re.I))
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    data["description"] = description
                
                # Extract key-value pairs
                for item in knowledge_panel.find_all(['div', 'span'], class_=re.compile(r'data|info|item|fact', re.I)):
                    text = item.get_text(strip=True)
                    if ':' in text and len(text) < 200:
                        key, value = text.split(':', 1)
                        data[key.strip()] = value.strip()
                
                # If we found description but no other data, return it
                if description and not data.get("description"):
                    data["description"] = description
                
                return data if data else None
        except Exception as e:
            logger.debug(f"Error extracting knowledge panel: {e}")
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract images from Google search results, especially from knowledge panel"""
        images = []
        try:
            # Look for knowledge panel images
            kp_images = soup.find_all('img', class_=re.compile(r'kno.*img|knowledge.*img|kp.*img', re.I))
            for img in kp_images:
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    images.append({
                        "url": src,
                        "source": "knowledge_panel",
                        "alt": img.get('alt', ''),
                        "type": "profile_image"
                    })
            
            # Look for main entity image
            main_img = soup.find('img', attrs={'data-attrid': 'image'})
            if main_img:
                src = main_img.get('src') or main_img.get('data-src')
                if src and src.startswith('http'):
                    images.append({
                        "url": src,
                        "source": "google_entity",
                        "alt": main_img.get('alt', ''),
                        "type": "entity_image"
                    })
            
            # Look for images in search results
            result_images = soup.find_all('img', class_=re.compile(r'result.*img|search.*img', re.I))
            for img in result_images[:3]:  # Limit to 3
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http') and 'googleusercontent' not in src:
                    images.append({
                        "url": src,
                        "source": "search_result",
                        "alt": img.get('alt', ''),
                        "type": "result_image"
                    })
            
            # Remove duplicates
            seen_urls = set()
            unique_images = []
            for img in images:
                if img['url'] not in seen_urls:
                    seen_urls.add(img['url'])
                    unique_images.append(img)
            
            return unique_images[:5]  # Return top 5 images
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
        return images
    
    def _extract_people_also_ask(self, soup: BeautifulSoup) -> List[str]:
        """Extract 'People Also Ask' questions"""
        questions = []
        try:
            paa_section = soup.find('div', class_=re.compile(r'people.*also|related.*questions', re.I))
            if paa_section:
                for question in paa_section.find_all(['div', 'span'], class_=re.compile(r'question|item', re.I)):
                    text = question.get_text(strip=True)
                    if text and '?' in text:
                        questions.append(text)
        except Exception as e:
            logger.debug(f"Error extracting people also ask: {e}")
        return questions[:5]  # Limit to 5 questions

google_search = GoogleSearch()

