from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3
        }
    
    def analyze_profile(self, results: Dict[str, Any], query: str, query_type: str) -> Dict[str, Any]:
        """Analyze all collected data and generate confidence report"""
        try:
            # Analyze Google search results for additional context
            google_analysis = self._analyze_google_results(results.get("google_search", {}), query)
            
            # Analyze blogs/articles for additional verification
            blog_analysis = self._analyze_blog_articles(results.get("web_scraper", {}), query)
            
            # Analyze news articles
            news_analysis = self._analyze_news_articles(results, query)
            
            analysis = {
                "query": query,
                "query_type": query_type,
                "analysis_date": datetime.utcnow().isoformat(),
                "data_sources": self._analyze_data_sources(results),
                "consistency_score": self._calculate_consistency(results, query),
                "verification_score": self._calculate_verification(results),
                "threat_indicators": self._identify_threat_indicators(results),
                "google_analysis": google_analysis,
                "blog_analysis": blog_analysis,
                "news_analysis": news_analysis,
                "confidence_level": "unknown",
                "confidence_score": 0.0,
                "key_findings": [],
                "recommendations": [],
                "risk_assessment": {},
                "data_quality": {}
            }
            
            # Calculate overall confidence (including Google search analysis)
            analysis["confidence_score"] = self._calculate_overall_confidence(analysis)
            analysis["confidence_level"] = self._get_confidence_level(analysis["confidence_score"])
            
            # Generate key findings (including Google insights)
            analysis["key_findings"] = self._generate_key_findings(results, analysis)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            # Risk assessment
            analysis["risk_assessment"] = self._assess_risk(results, analysis)
            
            # Data quality metrics
            analysis["data_quality"] = self._assess_data_quality(results)
            
            return analysis
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return {
                "error": str(e),
                "confidence_score": 0.0,
                "confidence_level": "unknown"
            }
    
    def _analyze_data_sources(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which data sources provided information"""
        sources = {
            "total_sources": 0,
            "active_sources": 0,
            "source_details": {},
            "coverage": {}
        }
        
        total_possible = 0
        active_count = 0
        
        # Include Google search in sources
        source_keys = list(results.keys())
        if "google_search" not in source_keys:
            source_keys.append("google_search")
        
        for api_name in source_keys:
            if api_name in ["image_matches", "correlation", "analysis"]:
                continue
            
            data = results.get(api_name)
            total_possible += 1
            has_data = data is not None and (
                (isinstance(data, dict) and len(data) > 0 and not (len(data) == 1 and "error" in data)) or
                (isinstance(data, list) and len(data) > 0)
            )
            
            if has_data:
                active_count += 1
                data_points = self._count_data_points(data)
                # Special handling for Google search
                if api_name == "google_search":
                    data_points = data.get("total", 0) or len(data.get("results", []))
                    if data.get("ai_summary"):
                        data_points += 1
                    if data.get("knowledge_panel"):
                        data_points += 1
                
                sources["source_details"][api_name] = {
                    "has_data": True,
                    "data_points": data_points,
                    "relevance": "high" if self._is_relevant(data) else "medium"
                }
            else:
                sources["source_details"][api_name] = {
                    "has_data": False,
                    "data_points": 0,
                    "relevance": "none"
                }
        
        sources["total_sources"] = total_possible
        sources["active_sources"] = active_count
        coverage_percentage = (active_count / total_possible * 100) if total_possible > 0 else 0
        sources["coverage"] = {
            "percentage": coverage_percentage,
            "rating": "excellent" if coverage_percentage >= 70 else 
                     "good" if coverage_percentage >= 50 else
                     "fair" if coverage_percentage >= 30 else "poor"
        }
        
        return sources
    
    def _count_data_points(self, data: Any) -> int:
        """Count number of data points in a result"""
        if not data:
            return 0
        if isinstance(data, dict):
            return len([v for v in data.values() if v])
        if isinstance(data, list):
            return len(data)
        return 1
    
    def _is_relevant(self, data: Any) -> bool:
        """Check if data is relevant (has substantial content)"""
        if not data:
            return False
        if isinstance(data, dict):
            return any(v for v in data.values() if v and (isinstance(v, str) and len(v) > 10))
        if isinstance(data, list):
            return len(data) > 0
        return True
    
    def _calculate_consistency(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Calculate consistency across different data sources"""
        consistency = {
            "score": 0.0,
            "factors": [],
            "matches": 0,
            "mismatches": 0
        }
        
        # Extract names, emails, usernames from different sources
        extracted_data = {
            "names": set(),
            "emails": set(),
            "usernames": set(),
            "locations": set(),
            "descriptions": set()
        }
        
        for api_name, data in results.items():
            if not data or not isinstance(data, dict):
                continue
            
            # Extract from Twitter
            if api_name == "twitter":
                if data.get("name"):
                    extracted_data["names"].add(data["name"].lower())
                if data.get("username"):
                    extracted_data["usernames"].add(data["username"].lower())
                if data.get("location"):
                    extracted_data["locations"].add(data["location"].lower())
            
            # Extract from Instagram
            if api_name in ["instagram", "instagram_scraper"]:
                if data.get("full_name") or data.get("name"):
                    extracted_data["names"].add((data.get("full_name") or data.get("name", "")).lower())
                if data.get("username"):
                    extracted_data["usernames"].add(data["username"].lower())
            
            # Extract from GitHub
            if api_name == "github":
                user = data.get("user", {})
                if user.get("name"):
                    extracted_data["names"].add(user["name"].lower())
                if user.get("login"):
                    extracted_data["usernames"].add(user["login"].lower())
            
            # Extract from Reddit
            if api_name == "reddit":
                if data.get("username"):
                    extracted_data["usernames"].add(data["username"].lower())
        
        # Calculate consistency
        total_unique = sum(len(v) for v in extracted_data.values())
        if total_unique > 0:
            # More matches = higher consistency
            matches = sum(1 for values in extracted_data.values() if len(values) > 1)
            consistency["matches"] = matches
            consistency["score"] = min(1.0, matches / max(1, total_unique - len([v for v in extracted_data.values() if len(v) == 0])))
        
        consistency["factors"] = [
            f"Found {len(extracted_data['names'])} unique names",
            f"Found {len(extracted_data['usernames'])} unique usernames",
            f"Found {len(extracted_data['emails'])} unique emails",
        ]
        
        return consistency
    
    def _calculate_verification(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate verification score based on multiple sources confirming same information"""
        verification = {
            "score": 0.0,
            "verified_items": [],
            "unverified_items": [],
            "verification_sources": 0
        }
        
        verified_count = 0
        total_items = 0
        
        # Check if same username appears in multiple platforms
        usernames = defaultdict(list)
        for api_name, data in results.items():
            if not data or not isinstance(data, dict):
                continue
            
            username = None
            if api_name == "twitter" and data.get("username"):
                username = data["username"].lower()
            elif api_name in ["instagram", "instagram_scraper"] and data.get("username"):
                username = data["username"].lower()
            elif api_name == "github" and data.get("user", {}).get("login"):
                username = data["user"]["login"].lower()
            elif api_name == "reddit" and data.get("username"):
                username = data["username"].lower()
            
            if username:
                usernames[username].append(api_name)
                total_items += 1
        
        # Username verified if appears in 2+ sources
        for username, sources in usernames.items():
            if len(sources) >= 2:
                verified_count += 1
                verification["verified_items"].append({
                    "item": username,
                    "sources": sources,
                    "verification_level": "high" if len(sources) >= 3 else "medium"
                })
            else:
                verification["unverified_items"].append({
                    "item": username,
                    "sources": sources
                })
        
        if total_items > 0:
            verification["score"] = verified_count / total_items
            verification["verification_sources"] = len([s for s in usernames.values() if len(s) >= 2])
        
        return verification
    
    def _identify_threat_indicators(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential threat indicators"""
        indicators = []
        
        # Check VirusTotal
        if results.get("virustotal"):
            vt_data = results["virustotal"]
            if isinstance(vt_data, dict):
                if vt_data.get("malicious_count", 0) > 0:
                    indicators.append({
                        "type": "malware",
                        "severity": "high",
                        "source": "virustotal",
                        "description": f"Found {vt_data.get('malicious_count')} malicious indicators",
                        "confidence": "high"
                    })
        
        # Check for suspicious patterns in usernames
        for api_name, data in results.items():
            if api_name in ["twitter", "instagram", "github", "reddit"] and data:
                username = None
                if isinstance(data, dict):
                    username = data.get("username") or data.get("user", {}).get("login")
                
                if username and self._is_suspicious_username(username):
                    indicators.append({
                        "type": "suspicious_pattern",
                        "severity": "medium",
                        "source": api_name,
                        "description": f"Suspicious username pattern: {username}",
                        "confidence": "medium"
                    })
        
        # Check for multiple account creation dates (potential fake accounts)
        creation_dates = []
        for api_name, data in results.items():
            if data and isinstance(data, dict):
                created = data.get("created_at") or data.get("created_utc") or data.get("user", {}).get("created_at")
                if created:
                    creation_dates.append(created)
        
        if len(creation_dates) > 3:
            indicators.append({
                "type": "multiple_accounts",
                "severity": "low",
                "source": "multiple",
                "description": f"Found {len(creation_dates)} accounts with different creation dates",
                "confidence": "medium"
            })
        
        return indicators
    
    def _is_suspicious_username(self, username: str) -> bool:
        """Check if username has suspicious patterns"""
        suspicious_patterns = [
            r'\d{4,}',  # Many numbers
            r'[._-]{2,}',  # Multiple separators
            r'^(admin|root|test|user)\d+',  # Common test patterns
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, username, re.I):
                return True
        return False
    
    def _analyze_google_results(self, google_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze Google search results for additional insights"""
        if not google_data:
            return {
                "has_data": False,
                "relevance_score": 0.0,
                "ai_summary_available": False,
                "result_count": 0,
                "content_richness": 0.0,
                "verification_sources": 0
            }
        
        analysis = {
            "has_data": True,
            "relevance_score": 0.0,
            "ai_summary_available": google_data.get("ai_summary") is not None,
            "result_count": google_data.get("total", 0) or len(google_data.get("results", [])),
            "knowledge_panel_available": google_data.get("knowledge_panel") is not None,
            "people_also_ask_count": len(google_data.get("people_also_ask", [])),
            "query_match_count": 0,
            "content_richness": 0.0,
            "verification_sources": 0,
            "detailed_description": False
        }
        
        # Analyze AI summary/content quality
        ai_summary = google_data.get("ai_summary", {})
        description = google_data.get("description") or (ai_summary.get("text") if ai_summary else None)
        knowledge_panel = google_data.get("knowledge_panel", {})
        
        if description:
            # Check description length and detail
            desc_length = len(description)
            if desc_length > 200:
                analysis["detailed_description"] = True
                analysis["content_richness"] += 0.3
            if desc_length > 500:
                analysis["content_richness"] += 0.2
            
            # Check for key information (dates, locations, affiliations)
            key_indicators = ["born", "died", "known for", "affiliated", "member of", "leader", "founded"]
            found_indicators = sum(1 for indicator in key_indicators if indicator in description.lower())
            analysis["content_richness"] += min(0.3, found_indicators * 0.05)
        
        # Analyze knowledge panel data
        if knowledge_panel:
            panel_keys = len(knowledge_panel.keys())
            analysis["content_richness"] += min(0.2, panel_keys * 0.05)
            analysis["verification_sources"] += 1
        
        # Calculate relevance based on query matches
        results = google_data.get("results", [])
        if results:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            matches = 0
            for r in results:
                title_lower = (r.get("title") or "").lower()
                snippet_lower = (r.get("snippet") or "").lower()
                text = title_lower + " " + snippet_lower
                
                # Check how many query words appear
                word_matches = sum(1 for word in query_words if word in text)
                if word_matches >= len(query_words) * 0.5:  # At least 50% of words match
                    matches += 1
            
            analysis["query_match_count"] = matches
            analysis["relevance_score"] = matches / len(results) if results else 0.0
            
            # Boost for multiple relevant results
            if matches >= 5:
                analysis["relevance_score"] = min(1.0, analysis["relevance_score"] + 0.2)
                analysis["verification_sources"] += matches
        
        # Boost confidence if AI summary is available
        if analysis["ai_summary_available"]:
            analysis["relevance_score"] = min(1.0, analysis["relevance_score"] + 0.3)
            analysis["content_richness"] += 0.3
        
        # Boost for knowledge panel
        if analysis["knowledge_panel_available"]:
            analysis["relevance_score"] = min(1.0, analysis["relevance_score"] + 0.2)
            analysis["verification_sources"] += 1
        
        analysis["content_richness"] = min(1.0, analysis["content_richness"])
        
        return analysis
    
    def _analyze_blog_articles(self, blog_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze blog and article content for verification"""
        if not blog_data or not isinstance(blog_data, dict):
            return {
                "has_data": False,
                "article_count": 0,
                "relevance_score": 0.0,
                "content_quality": 0.0,
                "verification_matches": 0
            }
        
        blogs = blog_data.get("blogs", [])
        if not blogs:
            return {
                "has_data": False,
                "article_count": 0,
                "relevance_score": 0.0,
                "content_quality": 0.0,
                "verification_matches": 0
            }
        
        analysis = {
            "has_data": True,
            "article_count": len(blogs),
            "relevance_score": 0.0,
            "content_quality": 0.0,
            "verification_matches": 0,
            "total_content_length": 0
        }
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        relevant_articles = 0
        total_content = 0
        matches_found = 0
        
        for blog in blogs:
            title = (blog.get("title") or "").lower()
            content = (blog.get("content") or blog.get("description") or "").lower()
            matches = blog.get("matches", [])
            
            # Check relevance
            title_words = set(title.split())
            content_words = set(content.split()[:100])  # First 100 words
            
            title_match = len(query_words.intersection(title_words)) / max(1, len(query_words))
            content_match = len(query_words.intersection(content_words)) / max(1, len(query_words))
            
            if title_match >= 0.5 or content_match >= 0.3:
                relevant_articles += 1
                matches_found += len(matches) if matches else 0
                total_content += len(content)
        
        if blogs:
            analysis["relevance_score"] = relevant_articles / len(blogs)
            analysis["verification_matches"] = matches_found
            analysis["total_content_length"] = total_content
            
            # Content quality based on length and matches
            if total_content > 5000:
                analysis["content_quality"] = 0.8
            elif total_content > 2000:
                analysis["content_quality"] = 0.6
            elif total_content > 500:
                analysis["content_quality"] = 0.4
            else:
                analysis["content_quality"] = 0.2
            
            # Boost for matches
            if matches_found > 0:
                analysis["content_quality"] = min(1.0, analysis["content_quality"] + (matches_found * 0.1))
        
        return analysis
    
    def _analyze_news_articles(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze news articles from multiple sources"""
        news_sources = ["newsapi", "googlenews"]
        analysis = {
            "has_data": False,
            "total_articles": 0,
            "relevance_score": 0.0,
            "source_count": 0,
            "recent_articles": 0
        }
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        all_articles = []
        
        for source in news_sources:
            data = results.get(source, {})
            if not data:
                continue
            
            articles = data.get("articles", [])
            if articles:
                analysis["has_data"] = True
                analysis["source_count"] += 1
                all_articles.extend(articles[:10])  # Limit per source
        
        if not all_articles:
            return analysis
        
        analysis["total_articles"] = len(all_articles)
        
        # Calculate relevance
        relevant_count = 0
        for article in all_articles:
            title = (article.get("title") or "").lower()
            description = (article.get("description") or article.get("snippet") or "").lower()
            text = title + " " + description
            
            # Check if query words appear
            word_matches = sum(1 for word in query_words if word in text)
            if word_matches >= len(query_words) * 0.4:  # At least 40% match
                relevant_count += 1
        
        if all_articles:
            analysis["relevance_score"] = relevant_count / len(all_articles)
        
        # Check for recent articles (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_count = 0
        
        for article in all_articles:
            published = article.get("publishedAt") or article.get("pubDate")
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    if pub_date > thirty_days_ago:
                        recent_count += 1
                except:
                    pass
        
        analysis["recent_articles"] = recent_count
        
        return analysis
    
    def _calculate_overall_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score with comprehensive analysis"""
        scores = []
        
        # Google search analysis (heavily weighted if available)
        google_analysis = analysis.get("google_analysis", {})
        blog_analysis = analysis.get("blog_analysis", {})
        news_analysis = analysis.get("news_analysis", {})
        
        # Calculate base Google score
        google_score = 0.0
        google_weight = 0.0
        
        if google_analysis.get("has_data"):
            if google_analysis.get("ai_summary_available"):
                # AI summary = high confidence base
                google_score = 0.70
                
                # Boost for detailed description
                if google_analysis.get("detailed_description"):
                    google_score += 0.10
                
                # Boost for content richness
                google_score += google_analysis.get("content_richness", 0) * 0.10
                
                # Boost for multiple verification sources
                verification_sources = google_analysis.get("verification_sources", 0)
                if verification_sources >= 5:
                    google_score += 0.10
                elif verification_sources >= 3:
                    google_score += 0.05
                
                # Boost for knowledge panel
                if google_analysis.get("knowledge_panel_available"):
                    google_score += 0.05
                
                # Boost for high relevance
                if google_analysis.get("relevance_score", 0) > 0.7:
                    google_score += 0.05
                
                google_score = min(1.0, google_score)
                google_weight = 0.35  # 35% weight for Google AI summary
            else:
                # Google results without AI summary
                google_relevance = google_analysis.get("relevance_score", 0)
                result_count = google_analysis.get("result_count", 0)
                
                if result_count > 0:
                    google_score = 0.35 + (google_relevance * 0.25)
                    google_score += min(0.15, google_analysis.get("content_richness", 0) * 0.15)
                    google_score = min(0.85, google_score)
                    google_weight = 0.25  # 25% weight for Google results
        else:
            google_weight = 0.0
        
        if google_weight > 0:
            scores.append(("google", google_score * google_weight))
        
        # Blog/Article analysis (15% weight)
        if blog_analysis.get("has_data"):
            blog_score = 0.0
            
            # Base score from relevance
            blog_score += blog_analysis.get("relevance_score", 0) * 0.4
            
            # Boost for content quality
            blog_score += blog_analysis.get("content_quality", 0) * 0.4
            
            # Boost for multiple articles
            article_count = blog_analysis.get("article_count", 0)
            if article_count >= 5:
                blog_score += 0.2
            elif article_count >= 3:
                blog_score += 0.1
            
            # Boost for verification matches
            if blog_analysis.get("verification_matches", 0) > 0:
                blog_score += 0.1
            
            blog_score = min(1.0, blog_score)
            scores.append(("blog_articles", blog_score * 0.15))
        else:
            scores.append(("blog_articles", 0.0 * 0.15))
        
        # News analysis (10% weight)
        if news_analysis.get("has_data"):
            news_score = 0.0
            
            # Base score from relevance
            news_score += news_analysis.get("relevance_score", 0) * 0.5
            
            # Boost for multiple sources
            if news_analysis.get("source_count", 0) >= 2:
                news_score += 0.2
            
            # Boost for multiple articles
            if news_analysis.get("total_articles", 0) >= 10:
                news_score += 0.2
            elif news_analysis.get("total_articles", 0) >= 5:
                news_score += 0.1
            
            # Boost for recent articles
            if news_analysis.get("recent_articles", 0) > 0:
                news_score += 0.1
            
            news_score = min(1.0, news_score)
            scores.append(("news", news_score * 0.10))
        else:
            scores.append(("news", 0.0 * 0.10))
        
        # Data coverage score (adjusted weight based on Google)
        if google_analysis.get("ai_summary_available"):
            coverage_weight = 0.12
        else:
            coverage_weight = 0.20
        
        coverage = analysis.get("data_sources", {}).get("coverage", {}).get("percentage", 0) / 100
        scores.append(("data_coverage", coverage * coverage_weight))
        
        # Consistency score
        consistency_weight = 0.12 if google_analysis.get("ai_summary_available") else 0.15
        consistency = analysis.get("consistency_score", {}).get("score", 0)
        scores.append(("consistency", consistency * consistency_weight))
        
        # Verification score
        verification_weight = 0.12 if google_analysis.get("ai_summary_available") else 0.15
        verification = analysis.get("verification_score", {}).get("score", 0)
        scores.append(("verification", verification * verification_weight))
        
        # Data quality score
        quality = analysis.get("data_quality", {}).get("overall_score", 0.5)
        scores.append(("data_quality", quality * 0.10))
        
        # Calculate total
        total_score = sum(score for _, score in scores)
        
        # Additional boosts
        # Boost if we have multiple independent verification sources
        verification_count = 0
        if google_analysis.get("verification_sources", 0) > 0:
            verification_count += google_analysis.get("verification_sources", 0)
        if blog_analysis.get("article_count", 0) > 0:
            verification_count += 1
        if news_analysis.get("source_count", 0) > 0:
            verification_count += news_analysis.get("source_count", 0)
        
        if verification_count >= 5:
            total_score = min(1.0, total_score + 0.05)
        elif verification_count >= 3:
            total_score = min(1.0, total_score + 0.03)
        
        # Minimum boost if Google AI summary is available
        if google_analysis.get("ai_summary_available") and total_score < 0.65:
            total_score = max(0.65, total_score)  # At least 65% if AI summary exists
        
        # Ensure score is in valid range
        return min(1.0, max(0.0, total_score))
    
    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level from score"""
        if score >= self.confidence_thresholds["high"]:
            return "high"
        elif score >= self.confidence_thresholds["medium"]:
            return "medium"
        elif score >= self.confidence_thresholds["low"]:
            return "low"
        return "very_low"
    
    def _generate_key_findings(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate key findings from the analysis"""
        findings = []
        
        # Google search findings
        google_analysis = analysis.get("google_analysis", {})
        if google_analysis.get("has_data"):
            if google_analysis.get("ai_summary_available"):
                findings.append("AI Summary available from Google - provides comprehensive overview")
                if google_analysis.get("detailed_description"):
                    findings.append("Detailed description found with rich content")
            if google_analysis.get("knowledge_panel_available"):
                findings.append("Knowledge Panel found - verified entity information available")
            if google_analysis.get("result_count", 0) > 0:
                findings.append(f"Found {google_analysis.get('result_count')} Google search results")
            if google_analysis.get("query_match_count", 0) > 0:
                findings.append(f"{google_analysis.get('query_match_count')} search results match the query")
            if google_analysis.get("verification_sources", 0) > 0:
                findings.append(f"{google_analysis.get('verification_sources')} independent verification sources found")
        
        # Blog/Article findings
        blog_analysis = analysis.get("blog_analysis", {})
        if blog_analysis.get("has_data"):
            article_count = blog_analysis.get("article_count", 0)
            findings.append(f"Found {article_count} relevant blog/article(s) with detailed information")
            if blog_analysis.get("verification_matches", 0) > 0:
                findings.append(f"{blog_analysis.get('verification_matches')} keyword matches found in articles")
            if blog_analysis.get("content_quality", 0) > 0.6:
                findings.append("High-quality content with substantial information")
        
        # News findings
        news_analysis = analysis.get("news_analysis", {})
        if news_analysis.get("has_data"):
            total_articles = news_analysis.get("total_articles", 0)
            source_count = news_analysis.get("source_count", 0)
            findings.append(f"Found {total_articles} news articles from {source_count} source(s)")
            if news_analysis.get("recent_articles", 0) > 0:
                findings.append(f"{news_analysis.get('recent_articles')} recent articles (last 30 days)")
        
        # Data coverage finding
        coverage = analysis.get("data_sources", {}).get("coverage", {})
        if coverage.get("percentage", 0) >= 70:
            findings.append(f"Excellent data coverage: {coverage.get('percentage', 0):.1f}% of sources returned data")
        elif coverage.get("percentage", 0) >= 50:
            findings.append(f"Good data coverage: {coverage.get('percentage', 0):.1f}% of sources returned data")
        else:
            findings.append(f"Limited data coverage: {coverage.get('percentage', 0):.1f}% of sources returned data")
        
        # Consistency finding
        consistency = analysis.get("consistency_score", {})
        if consistency.get("score", 0) >= 0.7:
            findings.append("High consistency across multiple data sources")
        elif consistency.get("score", 0) >= 0.5:
            findings.append("Moderate consistency across data sources")
        else:
            findings.append("Low consistency - data may be from different entities")
        
        # Verification finding
        verification = analysis.get("verification_score", {})
        if verification.get("verification_sources", 0) > 0:
            findings.append(f"{verification.get('verification_sources')} items verified across multiple platforms")
        
        # Threat indicators
        threats = analysis.get("threat_indicators", [])
        if threats:
            high_severity = [t for t in threats if t.get("severity") == "high"]
            if high_severity:
                findings.append(f"{len(high_severity)} high-severity threat indicator(s) found")
        
        return findings
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        confidence = analysis.get("confidence_score", 0)
        if confidence < 0.5:
            recommendations.append("Low confidence score - consider additional verification sources")
        
        coverage = analysis.get("data_sources", {}).get("coverage", {}).get("percentage", 0)
        if coverage < 50:
            recommendations.append("Expand search to additional data sources for better coverage")
        
        verification = analysis.get("verification_score", {})
        if verification.get("score", 0) < 0.5:
            recommendations.append("Verify identity across multiple platforms for higher confidence")
        
        threats = analysis.get("threat_indicators", [])
        if threats:
            recommendations.append("Review threat indicators and conduct further investigation")
        
        if not recommendations:
            recommendations.append("Profile analysis complete - data quality is good")
        
        return recommendations
    
    def _assess_risk(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level"""
        risk_score = 0.0
        risk_factors = []
        
        # Check threat indicators
        threats = analysis.get("threat_indicators", [])
        for threat in threats:
            if threat.get("severity") == "high":
                risk_score += 0.5
                risk_factors.append(threat.get("description"))
            elif threat.get("severity") == "medium":
                risk_score += 0.3
                risk_factors.append(threat.get("description"))
            else:
                risk_score += 0.1
        
        # Check VirusTotal results
        vt_data = results.get("virustotal", {})
        if vt_data and isinstance(vt_data, dict):
            malicious_count = vt_data.get("malicious_count", 0)
            if malicious_count > 0:
                risk_score += min(0.4, malicious_count * 0.1)
                risk_factors.append(f"VirusTotal: {malicious_count} malicious indicators")
        
        # Check for known threat keywords in Google AI summary
        google_data = results.get("google_search", {})
        if google_data:
            ai_summary = google_data.get("ai_summary", {})
            if ai_summary:
                summary_text = ai_summary.get("text", "").lower()
                threat_keywords = ["terrorist", "militant", "criminal", "wanted", "fugitive", "al-qaeda", "isis", "extremist"]
                if any(keyword in summary_text for keyword in threat_keywords):
                    risk_score += 0.4
                    risk_factors.append("Threat-related content found in Google AI summary")
        
        # Check data consistency (low consistency = higher risk, but only if no Google AI summary)
        google_analysis = analysis.get("google_analysis", {})
        if not google_analysis.get("ai_summary_available"):
            consistency = analysis.get("consistency_score", {}).get("score", 1.0)
            if consistency < 0.3:
                risk_score += 0.1
                risk_factors.append("Low data consistency - potential identity mismatch")
        
        risk_score = min(1.0, risk_score)
        
        risk_level = "low"
        if risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "factors": risk_factors,
            "assessment": self._get_risk_assessment_text(risk_level)
        }
    
    def _get_risk_assessment_text(self, level: str) -> str:
        assessments = {
            "high": "High risk - Multiple threat indicators detected. Immediate investigation recommended.",
            "medium": "Medium risk - Some concerning indicators found. Further monitoring advised.",
            "low": "Low risk - No significant threat indicators detected. Standard monitoring sufficient."
        }
        return assessments.get(level, "Risk assessment unavailable")
    
    def _assess_data_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of collected data"""
        quality = {
            "overall_score": 0.0,
            "completeness": 0.0,
            "accuracy": 0.0,
            "relevance": 0.0,
            "metrics": {}
        }
        
        total_sources = len([k for k in results.keys() if k not in ["image_matches", "correlation"]])
        sources_with_data = len([k for k, v in results.items() 
                                if k not in ["image_matches", "correlation"] and v and 
                                ((isinstance(v, dict) and len(v) > 0) or (isinstance(v, list) and len(v) > 0))])
        
        completeness = sources_with_data / total_sources if total_sources > 0 else 0
        quality["completeness"] = completeness
        
        # Accuracy based on verification
        verified_items = 0
        total_items = 0
        for data in results.values():
            if data and isinstance(data, dict):
                if data.get("username") or data.get("name"):
                    total_items += 1
                    # Assume verified if appears in multiple sources (simplified)
                    verified_items += 0.7  # Estimated
        
        accuracy = verified_items / total_items if total_items > 0 else 0.5
        quality["accuracy"] = accuracy
        
        # Relevance (simplified - based on data richness)
        relevant_sources = 0
        for data in results.values():
            if data and self._is_relevant(data):
                relevant_sources += 1
        
        relevance = relevant_sources / total_sources if total_sources > 0 else 0
        quality["relevance"] = relevance
        
        # Overall score
        quality["overall_score"] = (completeness * 0.4 + accuracy * 0.3 + relevance * 0.3)
        
        quality["metrics"] = {
            "sources_with_data": sources_with_data,
            "total_sources": total_sources,
            "data_richness": "high" if quality["overall_score"] > 0.7 else 
                            "medium" if quality["overall_score"] > 0.5 else "low"
        }
        
        return quality

analysis_engine = AnalysisEngine()

