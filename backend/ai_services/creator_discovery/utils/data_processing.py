# for data preprocessing

from typing import Dict, List, Any, Optional
import re
import json
from datetime import datetime
from ...shared.utils import clean_text, extract_hashtags, extract_mentions, calculate_engagement_rate

class CreatorDataProcessor:
    """Processes and normalizes creator data for AI consumption"""
    
    @staticmethod
    def normalize_creator_data(raw_data: Dict) -> Dict:
        """Normalize raw creator data to standard format"""
        try:
            normalized = {
                "id": raw_data.get("id") or raw_data.get("creator_id", ""),
                "name": clean_text(raw_data.get("name", "")),
                "handle": CreatorDataProcessor._normalize_handle(raw_data.get("handle", "")),
                "platform": raw_data.get("platform", "").title(),
                "bio": clean_text(raw_data.get("bio", "")),
                "followers": CreatorDataProcessor._normalize_number(raw_data.get("followers", 0)),
                "following": CreatorDataProcessor._normalize_number(raw_data.get("following", 0)),
                "total_posts": CreatorDataProcessor._normalize_number(raw_data.get("total_posts", 0)),
                "engagement_rate": CreatorDataProcessor._normalize_percentage(raw_data.get("engagement_rate", 0)),
                "categories": CreatorDataProcessor._normalize_categories(raw_data.get("categories", [])),
                "demographics": CreatorDataProcessor._normalize_demographics(raw_data.get("demographics", {})),
                "content_style": clean_text(raw_data.get("content_style", "")),
                "location": clean_text(raw_data.get("location", "")),
                "language": raw_data.get("language", "English"),
                "collaboration_rate": raw_data.get("collaboration_rate", ""),
                "response_rate": CreatorDataProcessor._normalize_percentage(raw_data.get("response_rate", 0)),
                "verified": bool(raw_data.get("verified", False)),
                "avg_likes": CreatorDataProcessor._normalize_number(raw_data.get("avg_likes", 0)),
                "avg_comments": CreatorDataProcessor._normalize_number(raw_data.get("avg_comments", 0)),
                "avg_shares": CreatorDataProcessor._normalize_number(raw_data.get("avg_shares", 0)),
                "profile_image_url": raw_data.get("profile_image_url", ""),
                "website_url": raw_data.get("website_url", ""),
                "email": raw_data.get("email", ""),
                "phone": raw_data.get("phone", ""),
                "created_at": CreatorDataProcessor._normalize_datetime(raw_data.get("created_at")),
                "updated_at": CreatorDataProcessor._normalize_datetime(raw_data.get("updated_at"))
            }
            
            # Calculate engagement rate if not provided
            if normalized["engagement_rate"] == 0 and normalized["followers"] > 0:
                normalized["engagement_rate"] = calculate_engagement_rate(
                    normalized["avg_likes"],
                    normalized["avg_comments"],
                    normalized["avg_shares"],
                    normalized["followers"]
                )
            
            return normalized
            
        except Exception as e:
            print(f"Error normalizing creator data: {e}")
            return raw_data
    
    @staticmethod
    def _normalize_handle(handle: str) -> str:
        """Normalize social media handle"""
        if not handle:
            return ""
        
        # Remove @ symbol if present
        handle = handle.lstrip("@")
        
        # Remove platform-specific prefixes
        handle = re.sub(r'^(instagram\\.com/|youtube\\.com/|tiktok\\.com/@|twitter\\.com/)', '', handle)
        
        return handle.strip()
    
    @staticmethod
    def _normalize_number(value: Any) -> int:
        """Normalize follower count or other numeric values"""
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            # Handle string numbers like "1.5M", "150K"
            value = value.upper().replace(",", "")
            
            if "K" in value:
                return int(float(value.replace("K", "")) * 1000)
            elif "M" in value:
                return int(float(value.replace("M", "")) * 1000000)
            elif "B" in value:
                return int(float(value.replace("B", "")) * 1000000000)
            else:
                try:
                    return int(value)
                except ValueError:
                    return 0
        
        return 0
    
    @staticmethod
    def _normalize_percentage(value: Any) -> float:
        """Normalize percentage values"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            value = value.replace("%", "").strip()
            try:
                return float(value)
            except ValueError:
                return 0.0
        
        return 0.0
    
    @staticmethod
    def _normalize_categories(categories: Any) -> List[str]:
        """Normalize category list"""
        if isinstance(categories, str):
            # Split string categories
            categories = [cat.strip() for cat in categories.split(",")]
        
        if isinstance(categories, list):
            return [clean_text(cat.lower()) for cat in categories if cat]
        
        return []
    
    @staticmethod
    def _normalize_demographics(demographics: Any) -> Dict:
        """Normalize demographics data"""
        if not isinstance(demographics, dict):
            return {}
        
        normalized_demo = {
            "age_group": demographics.get("age_group", ""),
            "gender_split": {},
            "top_locations": [],
            "primary_language": demographics.get("primary_language", "English")
        }
        
        # Normalize gender split
        gender_split = demographics.get("gender_split", {})
        if isinstance(gender_split, dict):
            for gender, percentage in gender_split.items():
                normalized_demo["gender_split"][gender.lower()] = CreatorDataProcessor._normalize_percentage(percentage)
        
        # Normalize locations
        locations = demographics.get("top_locations", [])
        if isinstance(locations, list):
            normalized_demo["top_locations"] = [clean_text(loc) for loc in locations if loc]
        elif isinstance(locations, str):
            normalized_demo["top_locations"] = [clean_text(loc.strip()) for loc in locations.split(",")]
        
        return normalized_demo
    
    @staticmethod
    def _normalize_datetime(dt_value: Any) -> Optional[str]:
        """Normalize datetime values"""
        if dt_value is None:
            return None
        
        if isinstance(dt_value, datetime):
            return dt_value.isoformat()
        
        if isinstance(dt_value, str):
            return dt_value
        
        return None
    
    @staticmethod
    def extract_content_features(content_sample: str) -> Dict:
        """Extract features from content sample for AI analysis"""
        try:
            if not content_sample:
                return {}
            
            features = {
                "hashtags": extract_hashtags(content_sample),
                "mentions": extract_mentions(content_sample),
                "word_count": len(content_sample.split()),
                "character_count": len(content_sample),
                "has_links": bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content_sample)),
                "has_emojis": bool(re.search(r'[\\U0001F600-\\U0001F64F\\U0001F300-\\U0001F5FF\\U0001F680-\\U0001F6FF\\U0001F1E0-\\U0001F1FF]', content_sample)),
                "question_count": content_sample.count("?"),
                "exclamation_count": content_sample.count("!"),
                "sentiment_indicators": CreatorDataProcessor._extract_sentiment_indicators(content_sample)
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting content features: {e}")
            return {}
    
    @staticmethod
    def _extract_sentiment_indicators(text: str) -> Dict:
        """Extract sentiment indicators from text"""
        positive_words = ["amazing", "awesome", "love", "great", "fantastic", "perfect", "wonderful", "excited", "happy", "best"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "disappointed", "sad", "angry", "frustrated"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        return {
            "positive_word_count": positive_count,
            "negative_word_count": negative_count,
            "positive_ratio": positive_count / max(total_words, 1),
            "negative_ratio": negative_count / max(total_words, 1),
            "overall_sentiment": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
        }
    
    @staticmethod
    def calculate_creator_quality_score(creator_data: Dict) -> float:
        """Calculate overall quality score for a creator"""
        try:
            score = 0.0
            
            # Engagement rate score (40% weight)
            engagement_rate = creator_data.get("engagement_rate", 0)
            engagement_score = min(engagement_rate / 10 * 40, 40)  # Max 40 points
            score += engagement_score
            
            # Follower count score (20% weight)
            followers = creator_data.get("followers", 0)
            if followers > 0:
                import math
                follower_score = min(math.log10(followers) * 4, 20)  # Max 20 points
                score += follower_score
            
            # Response rate score (20% weight)
            response_rate = creator_data.get("response_rate", 50)
            response_score = response_rate / 100 * 20  # Max 20 points
            score += response_score
            
            # Content quality indicators (20% weight)
            content_quality = 20  # Default score
            
            # Bonus for verified accounts
            if creator_data.get("verified", False):
                content_quality += 5
            
            # Bonus for complete profile
            profile_completeness = CreatorDataProcessor._calculate_profile_completeness(creator_data)
            content_quality += profile_completeness * 10  # Up to 10 bonus points
            
            score += min(content_quality, 20)
            
            return min(score, 100.0)  # Cap at 100
            
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 50.0  # Default score
    
    @staticmethod
    def _calculate_profile_completeness(creator_data: Dict) -> float:
        """Calculate profile completeness ratio"""
        required_fields = ["name", "bio", "categories", "location", "content_style"]
        completed_fields = 0
        
        for field in required_fields:
            if creator_data.get(field) and str(creator_data[field]).strip():
                completed_fields += 1
        
        return completed_fields / len(required_fields)
    
    @staticmethod
    def prepare_for_embedding(creator_data: Dict) -> str:
        """Prepare creator data for embedding generation"""
        try:
            text_parts = []
            
            # Basic information
            if creator_data.get("name"):
                text_parts.append(f"Creator name: {creator_data['name']}")
            
            if creator_data.get("platform"):
                text_parts.append(f"Platform: {creator_data['platform']}")
            
            # Content description
            if creator_data.get("content_style"):
                text_parts.append(f"Content style: {creator_data['content_style']}")
            
            if creator_data.get("bio"):
                text_parts.append(f"Bio: {creator_data['bio']}")
            
            # Categories
            categories = creator_data.get("categories", [])
            if categories:
                text_parts.append(f"Categories: {', '.join(categories)}")
            
            # Demographics
            demographics = creator_data.get("demographics", {})
            if demographics.get("age_group"):
                text_parts.append(f"Target audience age: {demographics['age_group']}")
            
            # Location and language
            if creator_data.get("location"):
                text_parts.append(f"Location: {creator_data['location']}")
            
            if creator_data.get("language"):
                text_parts.append(f"Language: {creator_data['language']}")
            
            # Performance metrics
            if creator_data.get("followers"):
                text_parts.append(f"Followers: {creator_data['followers']}")
            
            if creator_data.get("engagement_rate"):
                text_parts.append(f"Engagement rate: {creator_data['engagement_rate']}%")
            
            return ". ".join(text_parts)
            
        except Exception as e:
            print(f"Error preparing embedding text: {e}")
            return ""
    
    @staticmethod
    def validate_creator_data(creator_data: Dict) -> List[str]:
        """Validate creator data and return list of issues"""
        issues = []
        
        # Required fields
        required_fields = ["id", "name", "platform"]
        for field in required_fields:
            if not creator_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Validate follower count
        followers = creator_data.get("followers", 0)
        if not isinstance(followers, (int, float)) or followers < 0:
            issues.append("Invalid follower count")
        
        # Validate engagement rate
        engagement_rate = creator_data.get("engagement_rate", 0)
        if not isinstance(engagement_rate, (int, float)) or engagement_rate < 0 or engagement_rate > 100:
            issues.append("Invalid engagement rate (must be 0-100)")
        
        # Validate platform
        valid_platforms = ["Instagram", "YouTube", "TikTok", "Twitter", "LinkedIn", "Twitch", "Facebook"]
        platform = creator_data.get("platform", "")
        if platform and platform not in valid_platforms:
            issues.append(f"Invalid platform: {platform}")
        
        return issues