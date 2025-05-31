# backend/ai_services/ai_communication/utils/personalization.py

import re
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import json

class PersonalizationEngine:
    """Advanced personalization engine for creator outreach"""
    
    def __init__(self):
        self.personality_patterns = {
            "professional": ["business", "corporate", "professional", "formal"],
            "casual": ["fun", "casual", "friendly", "relaxed"],
            "creative": ["artistic", "creative", "innovative", "unique"],
            "technical": ["tech", "data", "analytics", "systematic"]
        }
        
        self.platform_styles = {
            "Instagram": {"tone": "visual", "max_length": 150, "hashtags": True},
            "YouTube": {"tone": "detailed", "max_length": 300, "hashtags": False},
            "TikTok": {"tone": "energetic", "max_length": 100, "hashtags": True},
            "LinkedIn": {"tone": "professional", "max_length": 250, "hashtags": False}
        }
    
    async def analyze_creator_personality(self, creator_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze creator's communication style and personality"""
        try:
            content_style = creator_profile.get('content_style', '').lower()
            bio = creator_profile.get('bio', '').lower()
            platform = creator_profile.get('platform', 'Instagram')
            
            # Determine personality type
            personality_scores = {}
            for personality, keywords in self.personality_patterns.items():
                score = sum(1 for keyword in keywords if keyword in content_style or keyword in bio)
                personality_scores[personality] = score
            
            dominant_personality = max(personality_scores, key=personality_scores.get)
            
            # Platform-specific adjustments
            platform_style = self.platform_styles.get(platform, self.platform_styles["Instagram"])
            
            return {
                "personality_type": dominant_personality,
                "personality_scores": personality_scores,
                "platform_style": platform_style,
                "communication_preferences": {
                    "tone": self._determine_tone(dominant_personality, platform),
                    "formality": self._determine_formality(dominant_personality),
                    "length": platform_style["max_length"],
                    "use_hashtags": platform_style["hashtags"]
                }
            }
        except Exception as e:
            # Fallback to default personality
            return {
                "personality_type": "casual",
                "platform_style": self.platform_styles.get(creator_profile.get('platform', 'Instagram')),
                "communication_preferences": {
                    "tone": "friendly",
                    "formality": "semi-formal",
                    "length": 150,
                    "use_hashtags": False
                }
            }
    
    def _determine_tone(self, personality: str, platform: str) -> str:
        """Determine appropriate tone based on personality and platform"""
        tone_mapping = {
            "professional": "formal",
            "casual": "friendly",
            "creative": "enthusiastic",
            "technical": "informative"
        }
        
        base_tone = tone_mapping.get(personality, "friendly")
        
        # Platform adjustments
        if platform == "TikTok":
            return "energetic"
        elif platform == "LinkedIn":
            return "professional"
        
        return base_tone
    
    def _determine_formality(self, personality: str) -> str:
        """Determine formality level"""
        if personality == "professional":
            return "formal"
        elif personality == "casual":
            return "informal"
        else:
            return "semi-formal"
    
    async def customize_message_for_creator(
        self, 
        base_message: str, 
        creator_profile: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> str:
        """Customize message based on creator's personality and preferences"""
        try:
            # Get creator personality analysis
            personality = personalization_data.get("personality_type", "casual")
            preferences = personalization_data.get("communication_preferences", {})
            
            # Apply tone adjustments
            tone = preferences.get("tone", "friendly")
            customized_message = self._adjust_message_tone(base_message, tone)
            
            # Apply length constraints
            max_length = preferences.get("length", 150)
            if len(customized_message) > max_length:
                customized_message = self._truncate_message(customized_message, max_length)
            
            # Add creator-specific touches
            customized_message = self._add_creator_specific_elements(
                customized_message, 
                creator_profile, 
                personality
            )
            
            return customized_message
            
        except Exception as e:
            return base_message  # Fallback to original message
    
    def _adjust_message_tone(self, message: str, tone: str) -> str:
        """Adjust message tone based on requirements"""
        tone_adjustments = {
            "formal": {
                "replacements": {
                    "hey": "Hello",
                    "awesome": "excellent",
                    "cool": "impressive",
                    "!": "."
                },
                "additions": ["I hope this message finds you well.", "Thank you for your time."]
            },
            "friendly": {
                "replacements": {
                    "Hello": "Hi",
                    "excellent": "amazing",
                    "impressive": "awesome"
                },
                "additions": ["Hope you're doing great!", "Looking forward to hearing from you!"]
            },
            "energetic": {
                "replacements": {
                    "Hello": "Hey!",
                    "good": "amazing",
                    "nice": "incredible"
                },
                "additions": ["This is so exciting!", "Can't wait to collaborate!"]
            }
        }
        
        adjustments = tone_adjustments.get(tone, tone_adjustments["friendly"])
        
        # Apply replacements
        adjusted_message = message
        for old, new in adjustments["replacements"].items():
            adjusted_message = adjusted_message.replace(old, new)
        
        return adjusted_message
    
    def _truncate_message(self, message: str, max_length: int) -> str:
        """Intelligently truncate message while preserving meaning"""
        if len(message) <= max_length:
            return message
        
        # Try to truncate at sentence boundaries
        sentences = message.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + ".") <= max_length - 3:  # Leave space for "..."
                truncated += sentence + "."
            else:
                break
        
        if truncated:
            return truncated.rstrip('.') + "..."
        else:
            # Hard truncate if no sentence boundaries work
            return message[:max_length-3] + "..."
    
    def _add_creator_specific_elements(
        self, 
        message: str, 
        creator_profile: Dict[str, Any], 
        personality: str
    ) -> str:
        """Add creator-specific personalization elements"""
        creator_name = creator_profile.get('name', 'there')
        platform = creator_profile.get('platform', 'Instagram')
        categories = creator_profile.get('categories', [])
        
        # Add name personalization
        if creator_name and creator_name != 'there':
            message = message.replace("Hi there", f"Hi {creator_name}")
            message = message.replace("Hello there", f"Hello {creator_name}")
        
        # Add platform-specific references
        platform_refs = {
            "Instagram": "your amazing posts",
            "YouTube": "your incredible videos", 
            "TikTok": "your viral content",
            "LinkedIn": "your professional content"
        }
        
        platform_ref = platform_refs.get(platform, "your content")
        
        # Add category-specific compliments
        if categories:
            category = categories[0] if categories else "content"
            category_compliments = {
                "fitness": "Your fitness journey is so inspiring!",
                "tech": "Your tech insights are really valuable!",
                "beauty": "Your beauty content is absolutely stunning!",
                "food": "Your food content makes me hungry every time!",
                "travel": "Your travel content is wanderlust-inducing!"
            }
            
            compliment = category_compliments.get(category.lower(), f"Your {category} content is amazing!")
            
            # Insert compliment naturally into message
            if "collaboration" in message.lower():
                message = message.replace(
                    "collaboration", 
                    f"collaboration. {compliment} This makes you a perfect fit for"
                )
        
        return message
    
    async def generate_follow_up_strategy(
        self, 
        creator_profile: Dict[str, Any],
        previous_interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized follow-up strategy"""
        try:
            interaction_count = len(previous_interactions)
            last_interaction = previous_interactions[-1] if previous_interactions else None
            
            if interaction_count == 0:
                # First interaction
                return {
                    "strategy": "initial_outreach",
                    "timing": "immediate",
                    "tone": "professional_friendly",
                    "focus": "introduction_and_opportunity"
                }
            elif interaction_count == 1:
                # First follow-up
                return {
                    "strategy": "gentle_reminder",
                    "timing": "3_days",
                    "tone": "casual_friendly",
                    "focus": "value_proposition"
                }
            elif interaction_count == 2:
                # Second follow-up
                return {
                    "strategy": "alternative_offer",
                    "timing": "1_week",
                    "tone": "understanding",
                    "focus": "flexibility_and_alternatives"
                }
            else:
                # Final follow-up
                return {
                    "strategy": "final_attempt",
                    "timing": "2_weeks",
                    "tone": "respectful_closure",
                    "focus": "future_opportunities"
                }
        except Exception as e:
            return {
                "strategy": "gentle_reminder",
                "timing": "3_days",
                "tone": "casual_friendly",
                "focus": "value_proposition"
            }
    
    def extract_engagement_insights(self, creator_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights about creator's engagement patterns"""
        try:
            engagement_rate = creator_profile.get('engagement_rate', 0)
            followers = creator_profile.get('followers', 0)
            platform = creator_profile.get('platform', 'Instagram')
            
            # Calculate engagement quality
            if engagement_rate > 5:
                quality = "excellent"
            elif engagement_rate > 3:
                quality = "good"
            elif engagement_rate > 1:
                quality = "average"
            else:
                quality = "below_average"
            
            # Determine audience size category
            if followers > 1000000:
                size_category = "mega"
            elif followers > 100000:
                size_category = "macro"
            elif followers > 10000:
                size_category = "micro"
            else:
                size_category = "nano"
            
            return {
                "engagement_quality": quality,
                "audience_size_category": size_category,
                "estimated_reach": int(followers * (engagement_rate / 100)),
                "influencer_tier": f"{size_category}_{quality}",
                "platform_performance": self._analyze_platform_performance(platform, engagement_rate)
            }
        except Exception as e:
            return {
                "engagement_quality": "average",
                "audience_size_category": "micro",
                "estimated_reach": 1000,
                "influencer_tier": "micro_average",
                "platform_performance": "standard"
            }
    
    def _analyze_platform_performance(self, platform: str, engagement_rate: float) -> str:
        """Analyze performance relative to platform benchmarks"""
        benchmarks = {
            "Instagram": 3.0,
            "YouTube": 2.0,
            "TikTok": 5.0,
            "LinkedIn": 2.5
        }
        
        benchmark = benchmarks.get(platform, 3.0)
        
        if engagement_rate > benchmark * 1.5:
            return "exceptional"
        elif engagement_rate > benchmark:
            return "above_average"
        elif engagement_rate > benchmark * 0.7:
            return "standard"
        else:
            return "below_average"
