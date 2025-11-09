import imagehash
from PIL import Image
import io
import requests
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from urllib.parse import urlparse

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available, using image hashing only")

logger = logging.getLogger(__name__)

class ImageMatcher:
    def __init__(self):
        self.image_cache = {}
        self.similarity_threshold = 0.85
        
    async def download_image(self, url: str) -> Optional[Image.Image]:
        try:
            if url in self.image_cache:
                return self.image_cache[url]
                
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            content = response.content
            img = Image.open(io.BytesIO(content))
            img = img.convert('RGB')
            
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            self.image_cache[url] = img
            return img
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None
    
    def calculate_hash(self, image: Image.Image) -> str:
        try:
            hash_value = imagehash.average_hash(image)
            return str(hash_value)
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return ""
    
    def calculate_similarity(self, hash1: str, hash2: str) -> float:
        try:
            if not hash1 or not hash2:
                return 0.0
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            similarity = 1 - (h1 - h2) / len(h1.hash) ** 2
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def extract_faces(self, image: Image.Image) -> List[np.ndarray]:
        if not FACE_RECOGNITION_AVAILABLE:
            return []
        try:
            img_array = np.array(image)
            face_locations = face_recognition.face_locations(img_array)
            faces = []
            for top, right, bottom, left in face_locations:
                face = img_array[top:bottom, left:right]
                faces.append(face)
            return faces
        except Exception as e:
            logger.error(f"Error extracting faces: {e}")
            return []
    
    def compare_faces(self, face1: np.ndarray, face2: np.ndarray) -> float:
        if not FACE_RECOGNITION_AVAILABLE:
            return 0.0
        try:
            encoding1 = face_recognition.face_encodings(face1)
            encoding2 = face_recognition.face_encodings(face2)
            
            if len(encoding1) == 0 or len(encoding2) == 0:
                return 0.0
            
            distance = face_recognition.face_distance([encoding1[0]], encoding2[0])[0]
            similarity = 1 - distance
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return 0.0
    
    async def find_matching_images(self, query_images: List[str], candidate_images: List[Dict[str, any]]) -> List[Dict[str, any]]:
        matches = []
        
        query_hashes = []
        for img_url in query_images:
            img = await self.download_image(img_url)
            if img:
                hash_value = self.calculate_hash(img)
                if hash_value:
                    query_hashes.append((img_url, hash_value, img))
        
        for candidate in candidate_images:
            candidate_url = candidate.get('url') or candidate.get('image_url') or candidate.get('thumbnail')
            if not candidate_url:
                continue
                
            candidate_img = await self.download_image(candidate_url)
            if not candidate_img:
                continue
                
            candidate_hash = self.calculate_hash(candidate_img)
            if not candidate_hash:
                continue
            
            max_similarity = 0.0
            best_match = None
            
            for query_url, query_hash, query_img in query_hashes:
                similarity = self.calculate_similarity(query_hash, candidate_hash)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = query_url
                
                if similarity > 0.7:
                    try:
                        query_faces = self.extract_faces(query_img)
                        candidate_faces = self.extract_faces(candidate_img)
                        
                        if query_faces and candidate_faces:
                            face_similarity = 0.0
                            for q_face in query_faces:
                                for c_face in candidate_faces:
                                    fs = self.compare_faces(q_face, c_face)
                                    face_similarity = max(face_similarity, fs)
                            
                            if face_similarity > 0.6:
                                similarity = max(similarity, face_similarity)
                                max_similarity = max(max_similarity, similarity)
                    except:
                        pass
            
            if max_similarity >= self.similarity_threshold:
                match = {
                    'url': candidate_url,
                    'similarity': max_similarity,
                    'source': candidate.get('source'),
                    'title': candidate.get('title'),
                    'context': candidate.get('context'),
                    'matched_with': best_match,
                    'type': 'high_match' if max_similarity > 0.9 else 'medium_match'
                }
                matches.append(match)
        
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
    
    def extract_images_from_html(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        images = []
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if not src:
                    continue
                
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                elif not src.startswith('http'):
                    src = urljoin(base_url, src)
                
                if 'data:image' in src or 'base64' in src:
                    continue
                
                alt = img.get('alt', '')
                images.append({
                    'url': src,
                    'alt': alt,
                    'source': base_url
                })
        except Exception as e:
            logger.error(f"Error extracting images from HTML: {e}")
        
        return images

image_matcher = ImageMatcher()

