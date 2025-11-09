from typing import Dict, List, Any, Tuple
from fuzzywuzzy import fuzz, process
import re
from collections import defaultdict

class CorrelationEngine:
    def __init__(self):
        self.name_similarity_threshold = 85
        self.email_similarity_threshold = 90
        self.location_similarity_threshold = 80
        
    def correlate_profiles(self, api_results: Dict[str, Any]) -> Dict[str, Any]:
        correlations = []
        entities = self._extract_entities(api_results)
        
        name_matches = self._match_names(entities.get("names", []))
        email_matches = self._match_emails(entities.get("emails", []))
        location_matches = self._match_locations(entities.get("locations", []))
        phone_matches = self._match_phones(entities.get("phones", []))
        username_matches = self._match_usernames(entities.get("usernames", []))
        
        all_matches = name_matches + email_matches + location_matches + phone_matches + username_matches
        merged_clusters = self._merge_clusters(all_matches)
        
        confidence_scores = self._calculate_confidence_scores(merged_clusters, api_results)
        
        return {
            "clusters": merged_clusters,
            "confidence_scores": confidence_scores,
            "total_connections": len(all_matches),
            "high_confidence_matches": [c for c in merged_clusters if c.get("confidence", 0) > 0.8]
        }
    
    def _extract_entities(self, api_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        entities = {
            "names": [],
            "emails": [],
            "phones": [],
            "locations": [],
            "usernames": [],
            "profiles": []
        }
        
        for api_name, data in api_results.items():
            if not data:
                continue
                
            source = {
                "api": api_name,
                "data": data
            }
            
            if api_name == "twitter" and isinstance(data, dict):
                if data.get("name"):
                    entities["names"].append({"value": data["name"], "source": source})
                if data.get("username"):
                    entities["usernames"].append({"value": data["username"], "source": source})
                if data.get("location"):
                    entities["locations"].append({"value": data["location"], "source": source})
                    
            elif api_name == "github" and isinstance(data, dict):
                user = data.get("user", {})
                if user.get("name"):
                    entities["names"].append({"value": user["name"], "source": source})
                if user.get("login"):
                    entities["usernames"].append({"value": user["login"], "source": source})
                if user.get("email"):
                    entities["emails"].append({"value": user["email"], "source": source})
                if user.get("location"):
                    entities["locations"].append({"value": user["location"], "source": source})
                    
            elif api_name == "hunter" and isinstance(data, dict):
                emails = data.get("emails", [])
                for email_data in emails if isinstance(emails, list) else [emails]:
                    if isinstance(email_data, dict) and email_data.get("value"):
                        entities["emails"].append({"value": email_data["value"], "source": source})
                        
            elif api_name == "numverify" and isinstance(data, dict):
                if data.get("number"):
                    entities["phones"].append({"value": data["number"], "source": source})
                if data.get("location"):
                    entities["locations"].append({"value": data["location"], "source": source})
        
        return entities
    
    def _match_names(self, names: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches = []
        processed = set()
        
        for i, name1 in enumerate(names):
            if name1["value"] in processed:
                continue
            cluster = [name1]
            
            for j, name2 in enumerate(names[i+1:], i+1):
                if name2["value"] in processed:
                    continue
                    
                similarity = fuzz.ratio(name1["value"].lower(), name2["value"].lower())
                if similarity >= self.name_similarity_threshold:
                    cluster.append(name2)
                    processed.add(name2["value"])
            
            if len(cluster) > 1:
                matches.append({
                    "type": "name",
                    "entities": cluster,
                    "confidence": min(100, max(cluster, key=lambda x: fuzz.ratio(name1["value"], x["value"])) if cluster else 0)
                })
                processed.add(name1["value"])
        
        return matches
    
    def _match_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches = []
        email_map = defaultdict(list)
        
        for email_data in emails:
            email_val = email_data["value"].lower()
            domain = email_val.split("@")[1] if "@" in email_val else ""
            email_map[domain].append(email_data)
        
        for domain, email_list in email_map.items():
            if len(email_list) > 1:
                matches.append({
                    "type": "email_domain",
                    "entities": email_list,
                    "confidence": 0.95
                })
        
        return matches
    
    def _match_phones(self, phones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches = []
        phone_map = defaultdict(list)
        
        for phone_data in phones:
            phone_val = re.sub(r'[^\d+]', '', phone_data["value"])
            phone_map[phone_val].append(phone_data)
        
        for phone, phone_list in phone_map.items():
            if len(phone_list) > 1:
                matches.append({
                    "type": "phone",
                    "entities": phone_list,
                    "confidence": 1.0
                })
        
        return matches
    
    def _match_usernames(self, usernames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches = []
        username_map = defaultdict(list)
        
        for username_data in usernames:
            username_val = username_data["value"].lower()
            username_map[username_val].append(username_data)
        
        for username, username_list in username_map.items():
            if len(username_list) > 1:
                matches.append({
                    "type": "username",
                    "entities": username_list,
                    "confidence": 0.98
                })
        
        return matches
    
    def _match_locations(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches = []
        processed = set()
        
        for i, loc1 in enumerate(locations):
            if loc1["value"] in processed:
                continue
            cluster = [loc1]
            
            for j, loc2 in enumerate(locations[i+1:], i+1):
                if loc2["value"] in processed:
                    continue
                    
                similarity = fuzz.ratio(loc1["value"].lower(), loc2["value"].lower())
                if similarity >= self.location_similarity_threshold:
                    cluster.append(loc2)
                    processed.add(loc2["value"])
            
            if len(cluster) > 1:
                matches.append({
                    "type": "location",
                    "entities": cluster,
                    "confidence": 0.75
                })
                processed.add(loc1["value"])
        
        return matches
    
    def _merge_clusters(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged = []
        used_indices = set()
        
        for i, match1 in enumerate(matches):
            if i in used_indices:
                continue
                
            cluster = match1["entities"].copy()
            cluster_type = match1["type"]
            confidence = match1.get("confidence", 0.5)
            
            for j, match2 in enumerate(matches[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                match1_sources = {e["source"]["api"] for e in match1["entities"]}
                match2_sources = {e["source"]["api"] for e in match2["entities"]}
                
                if match1_sources & match2_sources:
                    cluster.extend(match2["entities"])
                    confidence = max(confidence, match2.get("confidence", 0.5))
                    used_indices.add(j)
            
            if cluster:
                merged.append({
                    "type": cluster_type,
                    "entities": cluster,
                    "confidence": confidence,
                    "source_count": len(set(e["source"]["api"] for e in cluster))
                })
            used_indices.add(i)
        
        return merged
    
    def _calculate_confidence_scores(self, clusters: List[Dict[str, Any]], api_results: Dict[str, Any]) -> Dict[str, float]:
        scores = {}
        
        for cluster in clusters:
            entities = cluster["entities"]
            base_confidence = cluster.get("confidence", 0.5)
            source_count = cluster.get("source_count", 1)
            
            confidence_boost = min(0.3, source_count * 0.1)
            final_confidence = min(1.0, base_confidence + confidence_boost)
            
            for entity in entities:
                api_name = entity["source"]["api"]
                if api_name not in scores:
                    scores[api_name] = []
                scores[api_name].append(final_confidence)
        
        avg_scores = {api: sum(scores_list) / len(scores_list) if scores_list else 0.5 
                     for api, scores_list in scores.items()}
        
        return avg_scores

