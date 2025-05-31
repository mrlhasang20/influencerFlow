import google.generativeai as genai
from typing import Dict, List, Optional, Any
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings, GEMINI_CONFIG
from shared.utils import retry_async, Timer
from shared.redis_client import redis_client
import hashlib

class GeminiAIClient:
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.gemini_model
        self.generation_config = GEMINI_CONFIG.copy()
        
    @retry_async(max_retries=3, delay=1.0)
    async def generate_outreach_message(
        self,
        creator_profile: Dict,
        campaign_brief: Dict,
        message_type: str = "initial_outreach",
        custom_instructions: Optional[str] = None
    ) -> str:
        """Generate personalized outreach message for influencer"""
        
        try:
            with Timer(f"Generating {message_type} message"):
                # Check cache first
                cache_key = self._generate_cache_key(creator_profile, campaign_brief, message_type)
                cached_message = await redis_client.get_async(cache_key)
                if cached_message:
                    print("✅ Using cached outreach message")
                    return cached_message
                
                # Create comprehensive prompt
                prompt = self._create_outreach_prompt(
                    creator_profile, campaign_brief, message_type, custom_instructions
                )
                
                # Generate message using Gemini
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.generation_config["temperature"],
                        top_p=self.generation_config["top_p"],
                        top_k=self.generation_config["top_k"],
                        max_output_tokens=self.generation_config["max_output_tokens"]
                    ),
                    safety_settings=self.generation_config["safety_settings"]
                )
                
                print("=== RAW GEMINI RESPONSE ===")
                print(response)
                print("=== RESPONSE TEXT ===")
                print(response.text)
                
                message = response.text.strip()
                
                # Cache the generated message
                await redis_client.set_async(cache_key, message, ttl=3600)  # 1 hour cache
                
                return message
                
        except Exception as e:
            print(f"Error generating outreach message: {e}")
            # Return fallback message
            return self._generate_fallback_message(creator_profile, campaign_brief, message_type)
    
    def _create_outreach_prompt(
        self,
        creator_profile: Dict,
        campaign_brief: Dict,
        message_type: str,
        custom_instructions: Optional[str]
    ) -> str:
        """Create comprehensive prompt for outreach message generation"""
        
        base_prompt = f"""You are an expert influencer marketing manager. Generate a professional, personalized {message_type} message for an influencer collaboration.

CREATOR PROFILE:
- Name: {creator_profile.get('name', 'Creator')}
- Platform: {creator_profile.get('platform', 'Social Media')}
- Handle: {creator_profile.get('handle', '')}
- Followers: {creator_profile.get('followers', 0):,}
- Content Style: {creator_profile.get('content_style', 'Creative content')}
- Categories: {', '.join(creator_profile.get('categories', []))}
- Location: {creator_profile.get('location', 'Global')}
- Engagement Rate: {creator_profile.get('engagement_rate', 0)}%

CAMPAIGN DETAILS:
- Brand: {campaign_brief.get('brand_name', 'Brand')}
- Campaign: {campaign_brief.get('campaign_name', 'Campaign')}
- Product/Service: {campaign_brief.get('product_name', 'Product')}
- Campaign Goal: {campaign_brief.get('goal', 'Brand awareness')}
- Target Audience: {campaign_brief.get('target_audience', 'General audience')}
- Budget Range: {campaign_brief.get('budget_range', 'Competitive')}
- Timeline: {campaign_brief.get('timeline', 'Flexible')}
- Deliverables: {', '.join(campaign_brief.get('deliverables', ['Content creation']))}

MESSAGE TYPE: {message_type}

INSTRUCTIONS:
"""
        
        if message_type == "initial_outreach":
            base_prompt += """
- Start with a personalized greeting using the creator's name
- Reference their specific content or recent work to show genuine interest
- Clearly explain the collaboration opportunity
- Highlight why they're a perfect fit for this campaign
- Mention key campaign details (brand, product, timeline)
- Include next steps and contact information
- Keep the tone professional but friendly
- Ensure the message is concise (under 200 words)
- Include a clear call-to-action
"""
        elif message_type == "follow_up":
            base_prompt += """
- Acknowledge the previous outreach
- Add value with additional campaign details or incentives
- Show continued interest in collaboration
- Provide new compelling reasons to participate
- Include urgency if appropriate
- Offer to answer questions or provide more information
"""
        elif message_type == "negotiation":
            base_prompt += """
- Be professional and solution-oriented
- Acknowledge their proposal or concerns
- Present counter-offers or alternatives
- Explain the rationale behind terms
- Show flexibility where possible
- Maintain positive relationship tone
"""
        
        if custom_instructions:
            base_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"
        
        base_prompt += """

IMPORTANT GUIDELINES:
- Use the creator's actual name and platform
- Reference specific aspects of their content style
- Ensure compliance with advertising disclosure requirements
- Be authentic and avoid overly salesy language
- Respect cultural context and communication preferences
- Include proper business contact information
- Make the collaboration benefits clear for both parties

Generate a professional outreach message following these guidelines."""
        
        return base_prompt
    
    @retry_async(max_retries=3, delay=1.0)
    async def handle_negotiation(
        self,
        conversation_history: List[Dict],
        creator_proposal: Dict,
        brand_constraints: Dict,
        negotiation_strategy: str = "collaborative"
    ) -> Dict:
        """Handle AI-powered negotiation logic"""
        
        try:
            with Timer("AI negotiation processing"):
                # Create negotiation prompt
                prompt = self._create_negotiation_prompt(
                    conversation_history, creator_proposal, brand_constraints, negotiation_strategy
                )
                
                # Generate negotiation response
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,  # Lower temperature for more consistent negotiation
                        top_p=0.9,
                        top_k=40,
                        max_output_tokens=800
                    ),
                    safety_settings=self.generation_config["safety_settings"]
                )
                
                # Parse the structured response
                response_text = response.text.strip()
                
                # Try to parse as JSON, fallback to structured parsing
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return self._parse_negotiation_response(response_text)
                    
        except Exception as e:
            print(f"Error in AI negotiation: {e}")
            return self._generate_fallback_negotiation_response(creator_proposal, brand_constraints)
    
    def _create_negotiation_prompt(
        self,
        conversation_history: List[Dict],
        creator_proposal: Dict,
        brand_constraints: Dict,
        negotiation_strategy: str
    ) -> str:
        """Create prompt for negotiation handling"""
        
        conversation_summary = "\\n".join([
            f"{msg.get('sender', 'Unknown')}: {msg.get('message', '')}"
            for msg in conversation_history[-5:]  # Last 5 messages for context
        ])
        
        prompt = f"""You are an AI negotiation assistant for influencer marketing deals. Your goal is to find mutually beneficial agreements while staying within brand constraints.

NEGOTIATION STRATEGY: {negotiation_strategy}

BRAND CONSTRAINTS:
- Maximum Budget: ${brand_constraints.get('max_budget', 'Not specified')}
- Minimum Budget: ${brand_constraints.get('min_budget', 'Not specified')}
- Timeline Flexibility: {brand_constraints.get('timeline_flexibility', 'Moderate')}
- Required Deliverables: {', '.join(brand_constraints.get('required_deliverables', []))}
- Content Guidelines: {brand_constraints.get('content_guidelines', 'Standard')}
- Usage Rights: {brand_constraints.get('usage_rights', 'Campaign duration')}

CREATOR PROPOSAL:
- Requested Rate: ${creator_proposal.get('rate', 'Not specified')}
- Proposed Timeline: {creator_proposal.get('timeline', 'Not specified')}
- Proposed Deliverables: {', '.join(creator_proposal.get('deliverables', []))}
- Special Requirements: {creator_proposal.get('special_requirements', 'None')}
- Usage Rights Preference: {creator_proposal.get('usage_rights', 'Limited')}

CONVERSATION HISTORY:
{conversation_summary}

TASK: Analyze the creator's proposal against brand constraints and generate a negotiation response.

RESPONSE FORMAT (JSON):
{{
    "action": "accept|counter_offer|request_clarification|escalate",
    "message": "Professional response message to the creator",
    "proposed_terms": {{
        "rate": "proposed payment amount",
        "timeline": "proposed timeline",
        "deliverables": ["list of deliverables"],
        "usage_rights": "usage rights terms",
        "special_notes": "any special conditions"
    }},
    "justification": "Internal reasoning for the decision",
    "confidence_score": "0-100 confidence in this approach",
    "escalation_needed": true/false
}}

GUIDELINES:
- Be professional and solution-oriented
- Look for win-win opportunities
- Consider alternative value propositions
- Respect both parties' constraints
- Suggest creative solutions when possible
- Escalate only when necessary (major constraint violations)
- Maintain positive relationship tone

Generate the negotiation response:"""
        
        return prompt
    
    async def analyze_creator_content(
        self,
        content_samples: List[str],
        analysis_type: str = "brand_safety"
    ) -> Dict:
        """Analyze creator content for various insights"""
        
        try:
            with Timer(f"Content analysis - {analysis_type}"):
                prompt = self._create_content_analysis_prompt(content_samples, analysis_type)
                
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,  # Low temperature for consistent analysis
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=1000
                    ),
                    safety_settings=self.generation_config["safety_settings"]
                )
                
                analysis_text = response.text.strip()
                
                # Try to parse as JSON
                try:
                    return json.loads(analysis_text)
                except json.JSONDecodeError:
                    return {"analysis": analysis_text, "type": analysis_type}
                    
        except Exception as e:
            print(f"Error in content analysis: {e}")
            return {"error": str(e), "type": analysis_type}
    
    def _create_content_analysis_prompt(self, content_samples: List[str], analysis_type: str) -> str:
        """Create prompt for content analysis"""
        
        content_text = "\\n\\n---\\n\\n".join(content_samples[:5])  # Analyze up to 5 samples
        
        base_prompt = f"""Analyze the following creator content samples for {analysis_type}:

CONTENT SAMPLES:
{content_text}

ANALYSIS TYPE: {analysis_type}
"""
        
        if analysis_type == "brand_safety":
            base_prompt += """
Provide a brand safety analysis in JSON format:
{
    "safety_score": "0-100",
    "risk_factors": ["list of potential risks"],
    "positive_indicators": ["list of positive brand alignment factors"],
    "content_themes": ["main themes in content"],
    "language_analysis": {
        "tone": "professional|casual|humorous|etc",
        "appropriateness": "family_friendly|mature|adult",
        "language_quality": "0-100"
    },
    "recommendations": ["specific recommendations for brand partnership"]
}"""
        elif analysis_type == "audience_insights":
            base_prompt += """
Provide audience insights based on content style in JSON format:
{
    "likely_audience": {
        "age_range": "estimated age range",
        "interests": ["likely audience interests"],
        "demographics": "audience characteristics"
    },
    "content_style": {
        "format": "video|image|text|mixed",
        "tone": "description of tone",
        "themes": ["main content themes"]
    },
    "engagement_factors": ["what drives engagement"],
    "brand_alignment_potential": "0-100"
}"""
        elif analysis_type == "performance_prediction":
            base_prompt += """
Predict content performance in JSON format:
{
    "performance_prediction": {
        "engagement_likelihood": "high|medium|low",
        "viral_potential": "0-100",
        "audience_retention": "0-100"
    },
    "optimization_suggestions": ["suggestions to improve performance"],
    "best_posting_strategy": "recommended posting approach",
    "content_strengths": ["what works well"],
    "improvement_areas": ["areas for improvement"]
}"""
        
        return base_prompt
    
    def _generate_cache_key(self, creator_profile: Dict, campaign_brief: Dict, message_type: str) -> str:
        """Generate cache key for outreach messages"""
        key_data = {
            "creator_id": creator_profile.get("id", ""),
            "campaign_id": campaign_brief.get("id", ""),
            "message_type": message_type
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"outreach:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _generate_fallback_message(self, creator_profile: Dict, campaign_brief: Dict, message_type: str) -> str:
        """Generate fallback message when AI generation fails"""
        creator_name = creator_profile.get("name", "there")
        brand_name = campaign_brief.get("brand_name", "our brand")
        
        if message_type == "initial_outreach":
            return f"""Hi {creator_name},

I hope this message finds you well! I've been following your content and I'm impressed by your engaging {creator_profile.get('platform', 'social media')} presence.

I'm reaching out on behalf of {brand_name} about an exciting collaboration opportunity that I think would be a perfect fit for your audience.

We'd love to discuss the details with you. Would you be interested in learning more?

Best regards,
The {brand_name} Team

Please reply if you'd like to explore this partnership opportunity!"""
        
        return f"Hi {creator_name}, thank you for your interest in collaborating with {brand_name}. We'll be in touch with more details soon!"
    
    def _parse_negotiation_response(self, response_text: str) -> Dict:
        """Parse negotiation response from text format"""
        # Simple fallback parsing
        return {
            "action": "request_clarification",
            "message": response_text,
            "proposed_terms": {},
            "justification": "AI response parsing fallback",
            "confidence_score": 50,
            "escalation_needed": False
        }
    
    def _generate_fallback_negotiation_response(self, creator_proposal: Dict, brand_constraints: Dict) -> Dict:
        """Generate fallback negotiation response"""
        return {
            "action": "request_clarification",
            "message": "Thank you for your proposal. We're reviewing the details and will get back to you with our response shortly.",
            "proposed_terms": creator_proposal,
            "justification": "Fallback response due to AI processing error",
            "confidence_score": 30,
            "escalation_needed": True
        }