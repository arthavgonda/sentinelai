import os
import json
from typing import List, Dict, Optional, Any
import logging
import aiohttp

logger = logging.getLogger(__name__)

# Try to import Google Vision API (optional)
try:
    from google.cloud import vision
    from google.oauth2 import service_account
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logger.warning("Google Cloud Vision API not available. Install with: pip install google-cloud-vision")

class GoogleVisionService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Vision API client"""
        if not VISION_AVAILABLE:
            logger.warning("Google Vision API not available")
            self.client = None
            return
        
        try:
            service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "service-account.json")
            if os.path.exists(service_account_path):
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-vision']
                )
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info("Google Vision API client initialized successfully")
            else:
                logger.warning(f"Service account file not found at {service_account_path}")
                self.client = None
        except Exception as e:
            logger.error(f"Error initializing Google Vision API: {e}")
            self.client = None
    
    async def analyze_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Analyze an image using Google Vision API"""
        if not self.client or not VISION_AVAILABLE:
            return None
        
        try:
            # Download image asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return None
                    image_content = await response.read()
            
            # Prepare image for Vision API
            image = vision.Image(content=image_content)
            
            # Perform multiple detections (these are synchronous but fast)
            face_detection = self.client.face_detection(image=image)
            label_detection = self.client.label_detection(image=image)
            text_detection = self.client.text_detection(image=image)
            web_detection = self.client.web_detection(image=image)
            safe_search = self.client.safe_search_detection(image=image)
            
            result = {
                "faces": [],
                "labels": [],
                "text": [],
                "web_entities": [],
                "safe_search": {},
                "has_person": False
            }
            
            # Extract faces
            if face_detection.face_annotations:
                for face in face_detection.face_annotations:
                    result["faces"].append({
                        "joy": face.joy_likelihood.name,
                        "sorrow": face.sorrow_likelihood.name,
                        "anger": face.anger_likelihood.name,
                        "surprise": face.surprise_likelihood.name,
                        "headwear": face.headwear_likelihood.name,
                        "confidence": face.detection_confidence
                    })
                    result["has_person"] = True
            
            # Extract labels
            if label_detection.label_annotations:
                for label in label_detection.label_annotations:
                    result["labels"].append({
                        "description": label.description,
                        "score": label.score
                    })
                    if "person" in label.description.lower() or "face" in label.description.lower():
                        result["has_person"] = True
            
            # Extract text
            if text_detection.text_annotations:
                result["text"] = [annotation.description for annotation in text_detection.text_annotations[:5]]
            
            # Extract web entities
            if web_detection.web_detection:
                if web_detection.web_detection.web_entities:
                    for entity in web_detection.web_detection.web_entities[:10]:
                        result["web_entities"].append({
                            "description": entity.description,
                            "score": entity.score
                        })
            
            # Extract safe search
            if safe_search.safe_search_annotation:
                result["safe_search"] = {
                    "adult": safe_search.safe_search_annotation.adult.name,
                    "violence": safe_search.safe_search_annotation.violence.name,
                    "racy": safe_search.safe_search_annotation.racy.name
                }
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing image with Vision API: {e}")
            return None
    
    async def extract_images_from_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and analyze images from search results"""
        images = []
        
        try:
            # Extract from Google search (prioritize these)
            google_data = results.get("google_search", {})
            if google_data:
                # Get images from Google search results
                google_images = google_data.get("images", [])
                for img in google_images:
                    images.append({
                        "url": img.get("url"),
                        "source": img.get("source", "google_search"),
                        "type": img.get("type", "entity_image"),
                        "alt": img.get("alt", "")
                    })
            
            # Extract profile pictures from social media
            for api_name in ["twitter", "instagram", "instagram_scraper", "github", "reddit"]:
                data = results.get(api_name, {})
                if not data:
                    continue
                
                image_url = None
                if api_name in ["twitter", "instagram", "instagram_scraper"]:
                    # Handle both single profile and multiple profiles
                    if isinstance(data, dict):
                        if data.get("users") and isinstance(data.get("users"), list):
                            # Multiple users (from name search)
                            for user in data.get("users", [])[:3]:
                                img_url = user.get("profile_pic_url") or user.get("profile_image_url") or user.get("profile_image")
                                if img_url:
                                    images.append({
                                        "url": img_url,
                                        "source": api_name,
                                        "type": "profile_picture",
                                        "alt": user.get("name") or user.get("username", "")
                                    })
                        else:
                            # Single profile
                            image_url = data.get("profile_pic_url") or data.get("profile_image_url") or data.get("profile_image")
                elif api_name == "github":
                    user = data.get("user", {})
                    if user:
                        image_url = user.get("avatar_url")
                elif api_name == "reddit":
                    # Reddit doesn't typically provide profile pics in API
                    pass
                
                if image_url:
                    # Only add if not already added (for single profiles)
                    if api_name not in ["twitter", "instagram", "instagram_scraper"] or not data.get("users"):
                        images.append({
                            "url": image_url,
                            "source": api_name,
                            "type": "profile_picture"
                        })
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_images = []
            for img in images:
                if img.get("url") and img["url"] not in seen_urls:
                    seen_urls.add(img["url"])
                    unique_images.append(img)
            
            # Analyze images (limit to 3 to avoid rate limits)
            analyzed_images = []
            for img in unique_images[:3]:
                try:
                    if img.get("url"):
                        analysis = await self.analyze_image(img["url"])
                        if analysis:
                            img["analysis"] = analysis
                            analyzed_images.append(img)
                        else:
                            analyzed_images.append(img)  # Add without analysis
                except Exception as e:
                    logger.error(f"Error analyzing image {img.get('url')}: {e}")
                    analyzed_images.append(img)  # Add without analysis
            
            # Add remaining images without analysis
            analyzed_images.extend(unique_images[3:])
            
            return analyzed_images
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return images

google_vision = GoogleVisionService()

