# AI negotiation logic

from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
from .gemini_client import GeminiAIClient
from pathlib import Path
import sys

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import Timer, parse_budget_range
from shared.redis_client import redis_client
import json

class NegotiationAgent:
    def __init__(self):
        self.gemini_client = GeminiAIClient()
        self.negotiation_strategies = {
            "collaborative": "Win-win approach focusing on mutual benefits",
            "competitive": "Assertive approach prioritizing brand interests",
            "accommodating": "Flexible approach prioritizing relationship",
            "compromising": "Balanced approach seeking middle ground"
        }
    
    async def initiate_negotiation(
        self,
        creator_profile: Dict,
        campaign_brief: Dict,
        initial_offer: Dict
    ) -> Dict:
        """Initiate negotiation with a creator"""
        try:
            with Timer("Negotiation initiation"):
                # Create initial negotiation context
                negotiation_context = {
                    "negotiation_id": f"neg_{creator_profile.get('id', 'unknown')}_{int(datetime.now().timestamp())}",
                    "creator_profile": creator_profile,
                    "campaign_brief": campaign_brief,
                    "brand_constraints": self._extract_brand_constraints(campaign_brief),
                    "initial_offer": initial_offer,
                    "conversation_history": [],
                    "current_status": "initiated",
                    "strategy": "collaborative",
                    "created_at": datetime.now().isoformat()
                }
                
                # Generate initial offer message
                offer_message = await self._generate_initial_offer_message(
                    creator_profile, campaign_brief, initial_offer
                )
                
                # Store negotiation context
                await self._store_negotiation_context(negotiation_context)
                
                return {
                    "negotiation_id": negotiation_context["negotiation_id"],
                    "message": offer_message,
                    "offer_terms": initial_offer,
                    "status": "initiated"
                }
                
        except Exception as e:
            print(f"Error initiating negotiation: {e}")
            raise
    
    async def process_creator_response(
        self,
        negotiation_id: str,
        creator_response: Dict
    ) -> Dict:
        """Process creator's response and generate counter-offer or acceptance"""
        try:
            with Timer("Processing creator response"):
                # Load negotiation context
                context = await self._load_negotiation_context(negotiation_id)
                if not context:
                    raise ValueError(f"Negotiation {negotiation_id} not found")
                
                # Add creator response to conversation history
                context["conversation_history"].append({
                    "sender": "creator",
                    "message": creator_response.get("message", ""),
                    "proposal": creator_response.get("proposal", {}),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Analyze the response and determine action
                analysis = await self._analyze_creator_response(context, creator_response)
                
                # Generate appropriate response
                response = await self._generate_negotiation_response(context, analysis)
                
                # Update conversation history with brand response
                context["conversation_history"].append({
                    "sender": "brand",
                    "message": response["message"],
                    "proposal": response.get("proposed_terms", {}),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update context status
                context["current_status"] = response["action"]
                context["last_updated"] = datetime.now().isoformat()
                
                # Store updated context
                await self._store_negotiation_context(context)
                
                return response
                
        except Exception as e:
            print(f"Error processing creator response: {e}")
            raise
    
    async def _analyze_creator_response(self, context: Dict, creator_response: Dict) -> Dict:
        """Analyze creator's response to determine negotiation strategy"""
        try:
            creator_proposal = creator_response.get("proposal", {})
            brand_constraints = context["brand_constraints"]
            
            analysis = {
                "proposal_type": self._classify_proposal_type(creator_proposal),
                "budget_analysis": self._analyze_budget_proposal(creator_proposal, brand_constraints),
                "timeline_analysis": self._analyze_timeline_proposal(creator_proposal, brand_constraints),
                "deliverables_analysis": self._analyze_deliverables_proposal(creator_proposal, brand_constraints),
                "negotiation_tone": self._analyze_communication_tone(creator_response.get("message", "")),
                "recommendation": "accept|counter|escalate|clarify"
            }
            
            # Determine overall recommendation
            if analysis["budget_analysis"]["within_constraints"] and analysis["timeline_analysis"]["acceptable"]:
                analysis["recommendation"] = "accept"
            elif analysis["budget_analysis"]["negotiable"] or analysis["timeline_analysis"]["negotiable"]:
                analysis["recommendation"] = "counter"
            elif analysis["negotiation_tone"] == "aggressive" or not analysis["budget_analysis"]["reasonable"]:
                analysis["recommendation"] = "escalate"
            else:
                analysis["recommendation"] = "clarify"
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing creator response: {e}")
            return {"recommendation": "escalate", "error": str(e)}
    
    def _classify_proposal_type(self, proposal: Dict) -> str:
        """Classify the type of proposal from creator"""
        if not proposal:
            return "no_proposal"
        
        has_rate = "rate" in proposal or "budget" in proposal
        has_timeline = "timeline" in proposal or "deadline" in proposal
        has_deliverables = "deliverables" in proposal
        
        if has_rate and has_timeline and has_deliverables:
            return "comprehensive"
        elif has_rate:
            return "budget_focused"
        elif has_timeline:
            return "timeline_focused"
        elif has_deliverables:
            return "scope_focused"
        else:
            return "partial"
    
    def _analyze_budget_proposal(self, proposal: Dict, constraints: Dict) -> Dict:
        """Analyze budget proposal against constraints"""
        try:
            proposed_rate = proposal.get("rate", 0)
            if isinstance(proposed_rate, str):
                # Parse string rates like "$500" or "500"
                proposed_rate = float(proposed_rate.replace("$", "").replace(",", ""))
            
            max_budget = constraints.get("max_budget", 0)
            min_budget = constraints.get("min_budget", 0)
            
            within_constraints = min_budget <= proposed_rate <= max_budget
            negotiable = proposed_rate <= max_budget * 1.2  # 20% buffer for negotiation
            reasonable = proposed_rate <= max_budget * 2  # Reasonable if within 2x budget
            
            return {
                "proposed_rate": proposed_rate,
                "within_constraints": within_constraints,
                "negotiable": negotiable,
                "reasonable": reasonable,
                "budget_utilization": (proposed_rate / max_budget * 100) if max_budget > 0 else 0
            }
            
        except Exception as e:
            print(f"Error analyzing budget proposal: {e}")
            return {"within_constraints": False, "negotiable": False, "reasonable": False}
    
    def _analyze_timeline_proposal(self, proposal: Dict, constraints: Dict) -> Dict:
        """Analyze timeline proposal against constraints"""
        try:
            proposed_timeline = proposal.get("timeline", "")
            required_timeline = constraints.get("timeline", "")
            
            # Simple timeline analysis (in production, would use proper date parsing)
            timeline_acceptable = True  # Simplified for demo
            timeline_negotiable = True
            
            return {
                "proposed_timeline": proposed_timeline,
                "acceptable": timeline_acceptable,
                "negotiable": timeline_negotiable
            }
            
        except Exception as e:
            print(f"Error analyzing timeline proposal: {e}")
            return {"acceptable": True, "negotiable": True}
    
    def _analyze_deliverables_proposal(self, proposal: Dict, constraints: Dict) -> Dict:
        """Analyze deliverables proposal against constraints"""
        try:
            proposed_deliverables = proposal.get("deliverables", [])
            required_deliverables = constraints.get("required_deliverables", [])
            
            if isinstance(proposed_deliverables, str):
                proposed_deliverables = [proposed_deliverables]
            
            missing_required = [req for req in required_deliverables if req not in proposed_deliverables]
            additional_offered = [prop for prop in proposed_deliverables if prop not in required_deliverables]
            
            return {
                "proposed_deliverables": proposed_deliverables,
                "meets_requirements": len(missing_required) == 0,
                "missing_required": missing_required,
                "additional_offered": additional_offered,
                "acceptable": len(missing_required) <= 1  # Allow 1 missing for negotiation
            }
            
        except Exception as e:
            print(f"Error analyzing deliverables proposal: {e}")
            return {"meets_requirements": True, "acceptable": True}
    
    def _analyze_communication_tone(self, message: str) -> str:
        """Analyze the tone of creator's communication"""
        if not message:
            return "neutral"
        
        message_lower = message.lower()
        
        # Simple keyword-based tone analysis
        aggressive_keywords = ["demand", "must", "require", "insist", "non-negotiable"]
        professional_keywords = ["appreciate", "understand", "consider", "discuss"]
        friendly_keywords = ["excited", "love", "happy", "pleasure", "looking forward"]
        
        aggressive_count = sum(1 for keyword in aggressive_keywords if keyword in message_lower)
        professional_count = sum(1 for keyword in professional_keywords if keyword in message_lower)
        friendly_count = sum(1 for keyword in friendly_keywords if keyword in message_lower)
        
        if aggressive_count > professional_count + friendly_count:
            return "aggressive"
        elif friendly_count > professional_count:
            return "friendly"
        elif professional_count > 0:
            return "professional"
        else:
            return "neutral"
    
    async def _generate_negotiation_response(self, context: Dict, analysis: Dict) -> Dict:
        """Generate appropriate negotiation response based on analysis"""
        try:
            # Use Gemini AI for sophisticated response generation
            response = await self.gemini_client.handle_negotiation(
                conversation_history=context["conversation_history"],
                creator_proposal=context["conversation_history"][-1].get("proposal", {}),
                brand_constraints=context["brand_constraints"],
                negotiation_strategy=context.get("strategy", "collaborative")
            )
            
            # Ensure response has required fields
            if "action" not in response:
                response["action"] = analysis["recommendation"]
            
            if "message" not in response:
                response["message"] = await self._generate_fallback_message(context, analysis)
            
            return response
            
        except Exception as e:
            print(f"Error generating negotiation response: {e}")
            return await self._generate_fallback_response(context, analysis)
    
    async def _generate_fallback_message(self, context: Dict, analysis: Dict) -> str:
        """Generate fallback message when AI generation fails"""
        creator_name = context["creator_profile"].get("name", "there")
        
        if analysis["recommendation"] == "accept":
            return f"Hi {creator_name}, thank you for your proposal! We're pleased to accept your terms and move forward with the collaboration."
        elif analysis["recommendation"] == "counter":
            return f"Hi {creator_name}, thank you for your proposal. We'd like to discuss a few adjustments to better align with our campaign requirements."
        elif analysis["recommendation"] == "clarify":
            return f"Hi {creator_name}, thank you for your response. Could you please provide more details about your proposal so we can move forward?"
        else:
            return f"Hi {creator_name}, thank you for your proposal. We need to review this internally and will get back to you soon."
    
    async def _generate_fallback_response(self, context: Dict, analysis: Dict) -> Dict:
        """Generate fallback response structure"""
        return {
            "action": analysis["recommendation"],
            "message": await self._generate_fallback_message(context, analysis),
            "proposed_terms": context.get("initial_offer", {}),
            "justification": "Fallback response due to AI processing error",
            "confidence_score": 30,
            "escalation_needed": True
        }
    
    async def _generate_initial_offer_message(self, creator_profile: Dict, campaign_brief: Dict, initial_offer: Dict) -> str:
        """Generate initial offer message"""
        try:
            return await self.gemini_client.generate_outreach_message(
                creator_profile=creator_profile,
                campaign_brief=campaign_brief,
                message_type="negotiation",
                custom_instructions=f"Include these offer terms: {initial_offer}"
            )
        except Exception as e:
            print(f"Error generating initial offer message: {e}")
            creator_name = creator_profile.get("name", "there")
            brand_name = campaign_brief.get("brand_name", "our brand")
            return f"Hi {creator_name}, we'd love to collaborate with you on our {brand_name} campaign. Here are our proposed terms for your consideration."
    
    def _extract_brand_constraints(self, campaign_brief: Dict) -> Dict:
        """Extract brand constraints from campaign brief"""
        budget_range = campaign_brief.get("budget_range", "")
        budget_info = parse_budget_range(budget_range)
        
        return {
            "max_budget": budget_info.get("max", 0),
            "min_budget": budget_info.get("min", 0),
            "timeline": campaign_brief.get("timeline", ""),
            "required_deliverables": campaign_brief.get("deliverables", []),
            "content_guidelines": campaign_brief.get("content_guidelines", ""),
            "usage_rights": campaign_brief.get("usage_rights", "Campaign duration"),
            "timeline_flexibility": campaign_brief.get("timeline_flexibility", "Moderate")
        }
    
    async def _store_negotiation_context(self, context: Dict) -> bool:
        """Store negotiation context in Redis"""
        try:
            key = f"negotiation:{context['negotiation_id']}"
            return await redis_client.set_async(key, context, ttl=86400 * 7)  # 7 days
        except Exception as e:
            print(f"Error storing negotiation context: {e}")
            return False
    
    async def _load_negotiation_context(self, negotiation_id: str) -> Optional[Dict]:
        """Load negotiation context from Redis"""
        try:
            key = f"negotiation:{negotiation_id}"
            return await redis_client.get_async(key)
        except Exception as e:
            print(f"Error loading negotiation context: {e}")
            return None
    
    async def get_negotiation_status(self, negotiation_id: str) -> Dict:
        """Get current status of a negotiation"""
        try:
            context = await self._load_negotiation_context(negotiation_id)
            if not context:
                return {"error": "Negotiation not found"}
            
            return {
                "negotiation_id": negotiation_id,
                "status": context.get("current_status", "unknown"),
                "creator_name": context["creator_profile"].get("name", ""),
                "campaign_name": context["campaign_brief"].get("campaign_name", ""),
                "conversation_length": len(context.get("conversation_history", [])),
                "created_at": context.get("created_at", ""),
                "last_updated": context.get("last_updated", "")
            }
            
        except Exception as e:
            print(f"Error getting negotiation status: {e}")
            return {"error": str(e)}
    
    async def get_negotiation_history(self, negotiation_id: str) -> List[Dict]:
        """Get conversation history for a negotiation"""
        try:
            context = await self._load_negotiation_context(negotiation_id)
            if not context:
                return []
            
            return context.get("conversation_history", [])
            
        except Exception as e:
            print(f"Error getting negotiation history: {e}")
            return []