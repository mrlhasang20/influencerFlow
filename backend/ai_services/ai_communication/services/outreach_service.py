import sys
from pathlib import Path
import uuid

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional
import asyncio
import time
from datetime import datetime
from models.gemini_client import GeminiAIClient
from schemas.communication_schemas import (
    OutreachRequest, OutreachResponse, BatchOutreachRequest,
    BatchOutreachResponse, MessageType, CommunicationTone
)
from shared.utils import Timer, clean_text, generate_id
from shared.redis_client import redis_client
from shared.config import settings, GEMINI_CONFIG
from shared.database import get_db_session, Message

class OutreachService:
    def __init__(self):
        self.gemini_client = GeminiAIClient()
        self.message_templates = self._load_message_templates()
    
    async def generate_outreach_message(self, request: OutreachRequest) -> OutreachResponse:
        """Generate personalized outreach message"""
        start_time = time.time()
        
        try:
            with Timer(f"Outreach message generation - {request.message_type}"):
                # Generate the message using Gemini AI
                prompt = self._create_outreach_prompt(
                    request.creator_profile, request.campaign_brief, request.message_type.value, request.custom_instructions
                )
                print("\n=== PROMPT SENT TO GEMINI ===\n")
                print(prompt)
                print("\n=============================\n")
                
                # Clean and validate the message
                cleaned_message = clean_text(prompt)
                
                # Calculate message metrics
                word_count = len(cleaned_message.split())
                estimated_read_time = word_count / 200 * 60  # Assuming 200 WPM
                
                # Calculate personalization score
                personalization_score = self._calculate_personalization_score(
                    cleaned_message, request.creator_profile
                )
                
                # Perform compliance checks
                compliance_check = await self._perform_compliance_checks(
                    cleaned_message, request.campaign_brief
                )
                
                # Generate voice if requested
                voice_url = None
                has_voice = False
                if request.include_voice:
                    try:
                        # Voice generation would be implemented here
                        # For demo, we'll simulate it
                        voice_url = f"/audio/outreach_{generate_id()}.mp3"
                        has_voice = True
                    except Exception as e:
                        print(f"Voice generation failed: {e}")
                
                print("creator_profile:", request.creator_profile)
                print("campaign_brief:", request.campaign_brief)
                
                session = get_db_session()
                msg = Message(
                    id=str(uuid.uuid4()),
                    collaboration_id=request.collaboration_id,
                    sender="brand",
                    recipient=request.creator_profile.get("email"),
                    message_type="outreach",
                    content=cleaned_message
                )
                session.add(msg)
                session.commit()
                session.close()
                
                return OutreachResponse(
                    message=cleaned_message,
                    message_type=request.message_type,
                    tone=request.tone,
                    language=request.language,
                    word_count=word_count,
                    estimated_read_time=estimated_read_time,
                    has_voice=has_voice,
                    voice_url=voice_url,
                    personalization_score=personalization_score,
                    compliance_check=compliance_check
                )
                
        except Exception as e:
            print(f"Outreach generation error: {e}")
            # Return fallback message
            fallback_message = self._generate_fallback_message(request)
            return OutreachResponse(
                message=fallback_message,
                message_type=request.message_type,
                tone=request.tone,
                language=request.language,
                word_count=len(fallback_message.split()),
                estimated_read_time=len(fallback_message.split()) / 200 * 60,
                personalization_score=30.0,  # Low score for fallback
                compliance_check={"basic_check": True}
            )
    
    async def generate_batch_outreach(self, request: BatchOutreachRequest) -> BatchOutreachResponse:
        """Generate outreach messages for multiple creators"""
        start_time = time.time()
        batch_id = request.batch_id or generate_id("batch")
        
        try:
            with Timer(f"Batch outreach generation for {len(request.creator_profiles)} creators"):
                messages = []
                successful_generations = 0
                failed_generations = 0
                
                # Process creators in batches to avoid overwhelming the API
                batch_size = 5
                for i in range(0, len(request.creator_profiles), batch_size):
                    batch_creators = request.creator_profiles[i:i + batch_size]
                    
                    # Process batch concurrently
                    tasks = []
                    for creator_profile in batch_creators:
                        outreach_request = OutreachRequest(
                            creator_profile=creator_profile,
                            campaign_brief=request.campaign_brief,
                            message_type=request.message_type
                        )
                        tasks.append(self._generate_single_outreach_safe(outreach_request))
                    
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for creator_profile, result in zip(batch_creators, batch_results):
                        if isinstance(result, Exception):
                            failed_generations += 1
                            messages.append({
                                "creator_id": creator_profile.get("id", "unknown"),
                                "creator_name": creator_profile.get("name", "Unknown"),
                                "status": "failed",
                                "error": str(result)
                            })
                        else:
                            successful_generations += 1
                            messages.append({
                                "creator_id": creator_profile.get("id", "unknown"),
                                "creator_name": creator_profile.get("name", "Unknown"),
                                "status": "success",
                                "message": result.message,
                                "personalization_score": result.personalization_score,
                                "word_count": result.word_count
                            })
                    
                    # Small delay between batches to respect rate limits
                    if i + batch_size < len(request.creator_profiles):
                        await asyncio.sleep(1)
                
                processing_time = time.time() - start_time
                estimated_delivery_time = len(messages) * 0.5  # Estimate 0.5 seconds per message
                
                return BatchOutreachResponse(
                    batch_id=batch_id,
                    total_creators=len(request.creator_profiles),
                    successful_generations=successful_generations,
                    failed_generations=failed_generations,
                    messages=messages,
                    processing_time_seconds=processing_time,
                    estimated_delivery_time=estimated_delivery_time
                )
                
        except Exception as e:
            print(f"Batch outreach error: {e}")
            return BatchOutreachResponse(
                batch_id=batch_id,
                total_creators=len(request.creator_profiles),
                successful_generations=0,
                failed_generations=len(request.creator_profiles),
                messages=[],
                processing_time_seconds=time.time() - start_time
            )
    
    async def _generate_single_outreach_safe(self, request: OutreachRequest) -> OutreachResponse:
        """Safely generate single outreach message with error handling"""
        try:
            return await self.generate_outreach_message(request)
        except Exception as e:
            # Return minimal fallback response
            fallback_message = self._generate_fallback_message(request)
            return OutreachResponse(
                message=fallback_message,
                message_type=request.message_type,
                tone=request.tone,
                language=request.language,
                word_count=len(fallback_message.split()),
                estimated_read_time=len(fallback_message.split()) / 200 * 60,
                personalization_score=20.0,
                compliance_check={"basic_check": True}
            )
    
    def _calculate_personalization_score(self, message: str, creator_profile: Dict) -> float:
        """Calculate how personalized the message is"""
        try:
            score = 0.0
            message_lower = message.lower()
            
            # Check for creator name (20 points)
            creator_name = creator_profile.get("name", "").lower()
            if creator_name and creator_name in message_lower:
                score += 20
            
            # Check for platform mention (15 points)
            platform = creator_profile.get("platform", "").lower()
            if platform and platform in message_lower:
                score += 15
            
            # Check for content style reference (25 points)
            content_style = creator_profile.get("content_style", "").lower()
            if content_style:
                # Check if any keywords from content style appear in message
                style_keywords = content_style.split()[:5]  # First 5 words
                matches = sum(1 for keyword in style_keywords if keyword in message_lower)
                score += min(matches / len(style_keywords) * 25, 25)
            
            # Check for category mentions (20 points)
            categories = creator_profile.get("categories", [])
            if categories:
                category_matches = sum(1 for cat in categories if cat.lower() in message_lower)
                score += min(category_matches / len(categories) * 20, 20)
            
            # Check for location mention (10 points)
            location = creator_profile.get("location", "").lower()
            if location and any(loc in message_lower for loc in location.split()):
                score += 10
            
            # Check for handle mention (10 points)
            handle = creator_profile.get("handle", "").lower()
            if handle and handle in message_lower:
                score += 10
            
            return min(score, 100.0)
            
        except Exception as e:
            print(f"Error calculating personalization score: {e}")
            return 50.0  # Default score
    
    async def _perform_compliance_checks(self, message: str, campaign_brief: Dict) -> Dict[str, bool]:
        """Perform compliance checks on the message"""
        try:
            checks = {
                "has_disclosure": False,
                "professional_tone": True,
                "no_spam_keywords": True,
                "appropriate_length": True,
                "clear_next_steps": False
            }
            
            message_lower = message.lower()
            
            # Check for disclosure indicators
            disclosure_keywords = ["collaboration", "partnership", "sponsored", "paid", "advertisement"]
            checks["has_disclosure"] = any(keyword in message_lower for keyword in disclosure_keywords)
            
            # Check for spam keywords
            spam_keywords = ["guaranteed", "limited time", "act now", "exclusive deal"]
            checks["no_spam_keywords"] = not any(keyword in message_lower for keyword in spam_keywords)
            
            # Check message length (should be between 50-300 words)
            word_count = len(message.split())
            checks["appropriate_length"] = 50 <= word_count <= 300
            
            # Check for clear next steps
            next_step_indicators = ["reply", "respond", "contact", "reach out", "let me know", "interested"]
            checks["clear_next_steps"] = any(indicator in message_lower for indicator in next_step_indicators)
            
            return checks
            
        except Exception as e:
            print(f"Error performing compliance checks: {e}")
            return {"basic_check": True}
    
    def _generate_fallback_message(self, request: OutreachRequest) -> str:
        """Generate fallback message when AI generation fails"""
        creator_name = request.creator_profile.get("name", "there")
        brand_name = request.campaign_brief.get("brand_name", "our brand")
        platform = request.creator_profile.get("platform", "social media")
        
        if request.message_type == MessageType.INITIAL_OUTREACH:
            return f"""Hi {creator_name},

I hope this message finds you well! I've been following your {platform} content and I'm impressed by your engaging presence.

I'm reaching out on behalf of {brand_name} about an exciting collaboration opportunity that I think would be a perfect fit for your audience.

We'd love to discuss the details with you. Would you be interested in learning more about this partnership?

Best regards,
The {brand_name} Team

Please reply if you'd like to explore this opportunity further!"""
        
        elif request.message_type == MessageType.FOLLOW_UP:
            return f"""Hi {creator_name},

I wanted to follow up on my previous message about the {brand_name} collaboration opportunity.

I understand you're likely busy with your content creation, but I didn't want you to miss out on this exciting partnership.

If you're interested, I'd be happy to share more details about the campaign and how we can work together.

Looking forward to hearing from you!

Best regards,
The {brand_name} Team"""
        
        else:
            return f"Hi {creator_name}, thank you for your interest in collaborating with {brand_name}. We'll be in touch with more details soon!"
    
    def _load_message_templates(self) -> Dict[str, str]:
        """Load message templates for different scenarios"""
        return {
            "initial_outreach": """
Hi {creator_name},

I hope this message finds you well! I've been following your {platform} content, particularly your work in {categories}, and I'm impressed by {specific_compliment}.

I'm reaching out on behalf of {brand_name} about an exciting collaboration opportunity for our {campaign_name} campaign. We're looking for creators who {target_criteria}, and you're exactly what we're looking for.

Here's what we have in mind:
- {deliverables}
- Timeline: {timeline}
- Compensation: {budget_range}

We believe this partnership would be a perfect fit for your audience and align beautifully with your content style.

Would you be interested in learning more? I'd love to hop on a quick call to discuss the details.

Best regards,
{sender_name}
{brand_name} Team

P.S. Feel free to check out our previous collaborations at {website_url}
            """,
            
            "follow_up": """
Hi {creator_name},

I hope you're doing well! I wanted to follow up on my message about the {brand_name} collaboration opportunity.

I know how busy you must be creating amazing content for your audience, so I wanted to make sure this exciting partnership didn't slip through the cracks.

To sweeten the deal, we're also offering:
- {additional_benefits}
- Flexible timeline to work with your schedule
- Full creative control over the content

This campaign has been performing amazingly well with other creators in your space, and we'd hate for you to miss out!

If you're interested, just reply to this message and we can set up a quick chat.

Looking forward to potentially working together!

Best,
{sender_name}
            """,
            
            "contract_offer": """
Hi {creator_name},

Thank you for your interest in our {campaign_name} collaboration! We're excited to move forward with you.

Based on our discussion, here are the agreed terms:
- Deliverables: {deliverables}
- Timeline: {timeline}
- Compensation: {final_amount}
- Usage rights: {usage_rights}

I've attached the collaboration agreement for your review. Please take a look and let me know if you have any questions.

Once you're ready to proceed, simply sign and return the agreement, and we'll get this exciting partnership started!

Thank you for choosing to work with {brand_name}. We can't wait to see what you create!

Best regards,
{sender_name}
{brand_name} Team
            """
        }
    
    async def get_message_suggestions(self, creator_profile: Dict, campaign_brief: Dict) -> List[str]:
        """Get message suggestions for manual customization"""
        try:
            suggestions = []
            
            # Personalization suggestions
            if creator_profile.get("content_style"):
                suggestions.append(f"Reference their {creator_profile['content_style']}")
            
            if creator_profile.get("categories"):
                categories = ", ".join(creator_profile["categories"][:2])
                suggestions.append(f"Mention their expertise in {categories}")
            
            if creator_profile.get("location"):
                suggestions.append(f"Reference their location ({creator_profile['location']})")
            
            # Campaign-specific suggestions
            if campaign_brief.get("target_audience"):
                suggestions.append(f"Highlight audience alignment with {campaign_brief['target_audience']}")
            
            if campaign_brief.get("unique_selling_points"):
                suggestions.append("Emphasize unique campaign benefits")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            print(f"Error getting message suggestions: {e}")
            return ["Use their name", "Mention their platform", "Reference their content style"]

def map_creator_to_profile(creator):
    return {
        'name': creator.get('name', 'Creator'),
        'platform': creator.get('platform', 'Social Media'),
        'handle': creator.get('handle', ''),
        'followers': creator.get('followers', 0),
        'content_style': creator.get('content_style', 'Creative content'),
        'categories': creator.get('categories', []),
        'location': creator.get('location', 'Global'),
        'engagement_rate': creator.get('engagement_rate', 0),
        'audience_demographics': str(creator.get('demographics', 'N/A')),
        # Add more fields as needed
    }

def map_request_to_campaign_brief(request_data):
    return {
        'brand_name': request_data.get('brand_name', 'Our Brand'),
        'campaign_name': request_data.get('campaign_name', 'Exciting New Campaign'),
        'target_audience': request_data.get('target_audience', 'General audience'),
        'budget_range': request_data.get('budget_range', 'Competitive'),
        'timeline': request_data.get('timeline', 'Flexible'),
        'goal': ', '.join(request_data.get('campaign_goals', ['Brand awareness'])),
        'desired_content': ', '.join(request_data.get('content_types', ['a creative post'])),
        # Add more fields as needed
    }