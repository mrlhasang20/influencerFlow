from typing import List, Dict, Optional
import asyncio
import time
from datetime import datetime
from models.negotiation_agent import NegotiationAgent
from schemas.communication_schemas import (
    NegotiationRequest, NegotiationResponse, NegotiationMetrics,
    NegotiationAction, NegotiationStrategy
)
import sys

from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import Timer, generate_id, parse_budget_range
from shared.redis_client import redis_client

class NegotiationService:
    def __init__(self):
        self.negotiation_agent = NegotiationAgent()
        self.active_negotiations = {}
    
    async def start_negotiation(self, request: NegotiationRequest) -> NegotiationResponse:
        """Start a new negotiation process"""
        try:
            with Timer("Starting new negotiation"):
                # Extract initial offer from campaign brief
                initial_offer = self._extract_initial_offer(request.campaign_brief, request.brand_constraints)
                
                # Start negotiation using the agent
                negotiation_result = await self.negotiation_agent.initiate_negotiation(
                    creator_profile=request.creator_profile,
                    campaign_brief=request.campaign_brief,
                    initial_offer=initial_offer
                )
                
                # Create response
                response = NegotiationResponse(
                    negotiation_id=negotiation_result["negotiation_id"],
                    action=NegotiationAction.COUNTER_OFFER,
                    message=negotiation_result["message"],
                    proposed_terms=negotiation_result["offer_terms"],
                    justification="Initial negotiation offer based on campaign requirements",
                    confidence_score=85.0,
                    escalation_needed=False,
                    alternative_options=[],
                    estimated_success_rate=75.0,
                    next_steps=[
                        "Wait for creator response",
                        "Review creator proposal",
                        "Prepare counter-offer if needed"
                    ]
                )
                
                # Store negotiation metrics
                await self._initialize_negotiation_metrics(response.negotiation_id, request)
                
                return response
                
        except Exception as e:
            print(f"Error starting negotiation: {e}")
            raise
    
    async def process_negotiation_response(self, request: NegotiationRequest) -> NegotiationResponse:
        """Process creator's response and generate counter-response"""
        try:
            with Timer("Processing negotiation response"):
                if not request.negotiation_id:
                    raise ValueError("Negotiation ID required for response processing")
                
                if not request.creator_response:
                    raise ValueError("Creator response required")
                
                # Process the response using the negotiation agent
                agent_response = await self.negotiation_agent.process_creator_response(
                    negotiation_id=request.negotiation_id,
                    creator_response=request.creator_response
                )
                
                # Convert agent response to service response
                response = NegotiationResponse(
                    negotiation_id=request.negotiation_id,
                    action=NegotiationAction(agent_response.get("action", "request_clarification")),
                    message=agent_response.get("message", ""),
                    proposed_terms=agent_response.get("proposed_terms", {}),
                    justification=agent_response.get("justification", ""),
                    confidence_score=agent_response.get("confidence_score", 50.0),
                    escalation_needed=agent_response.get("escalation_needed", False),
                    alternative_options=await self._generate_alternative_options(request, agent_response),
                    estimated_success_rate=self._calculate_success_rate(request, agent_response),
                    next_steps=self._generate_next_steps(agent_response)
                )
                
                # Update negotiation metrics
                await self._update_negotiation_metrics(request.negotiation_id, request, response)
                
                return response
                
        except Exception as e:
            print(f"Error processing negotiation response: {e}")
            raise
    
    async def get_negotiation_status(self, negotiation_id: str) -> Dict:
        """Get current status of a negotiation"""
        try:
            status = await self.negotiation_agent.get_negotiation_status(negotiation_id)
            return status
        except Exception as e:
            print(f"Error getting negotiation status: {e}")
            return {"error": str(e)}
    
    async def get_negotiation_history(self, negotiation_id: str) -> List[Dict]:
        """Get conversation history for a negotiation"""
        try:
            history = await self.negotiation_agent.get_negotiation_history(negotiation_id)
            return history
        except Exception as e:
            print(f"Error getting negotiation history: {e}")
            return []
    
    async def get_negotiation_metrics(self, negotiation_id: str) -> Optional[NegotiationMetrics]:
        """Get metrics for a specific negotiation"""
        try:
            metrics_key = f"negotiation_metrics:{negotiation_id}"
            metrics_data = await redis_client.get_async(metrics_key)
            
            if metrics_data:
                return NegotiationMetrics(**metrics_data)
            return None
            
        except Exception as e:
            print(f"Error getting negotiation metrics: {e}")
            return None
    
    async def end_negotiation(self, negotiation_id: str, final_terms: Dict, outcome: str) -> bool:
        """End a negotiation with final terms"""
        try:
            # Update negotiation status
            context_key = f"negotiation:{negotiation_id}"
            context = await redis_client.get_async(context_key)
            
            if context:
                context["current_status"] = "completed"
                context["final_terms"] = final_terms
                context["outcome"] = outcome
                context["completed_at"] = datetime.now().isoformat()
                
                await redis_client.set_async(context_key, context, ttl=86400 * 30)  # 30 days
            
            # Update metrics
            await self._finalize_negotiation_metrics(negotiation_id, outcome, final_terms)
            
            return True
            
        except Exception as e:
            print(f"Error ending negotiation: {e}")
            return False
    
    def _extract_initial_offer(self, campaign_brief: Dict, brand_constraints: Dict) -> Dict:
        """Extract initial offer terms from campaign brief"""
        try:
            # Parse budget information
            budget_range = campaign_brief.get("budget_range", "")
            budget_info = parse_budget_range(budget_range)
            
            # Start with lower end of budget range for negotiation
            initial_rate = budget_info.get("min", 0)
            if initial_rate == 0:
                initial_rate = budget_info.get("max", 1000) * 0.7  # Start at 70% of max
            
            initial_offer = {
                "rate": initial_rate,
                "timeline": campaign_brief.get("timeline", "2-3 weeks"),
                "deliverables": campaign_brief.get("deliverables", ["Social media post"]),
                "usage_rights": brand_constraints.get("usage_rights", "Campaign duration"),
                "payment_terms": brand_constraints.get("payment_terms", "Net 30"),
                "revisions": brand_constraints.get("max_revisions", 2),
                "exclusivity": brand_constraints.get("exclusivity", "Category exclusive for 30 days")
            }
            
            return initial_offer
            
        except Exception as e:
            print(f"Error extracting initial offer: {e}")
            return {
                "rate": 500,
                "timeline": "2-3 weeks",
                "deliverables": ["Social media post"],
                "usage_rights": "Campaign duration"
            }
    
    async def _generate_alternative_options(self, request: NegotiationRequest, agent_response: Dict) -> List[Dict]:
        """Generate alternative negotiation options"""
        try:
            alternatives = []
            
            # Budget alternatives
            current_offer = agent_response.get("proposed_terms", {})
            current_rate = current_offer.get("rate", 0)
            
            if current_rate > 0:
                # Higher budget option
                alternatives.append({
                    "type": "budget_increase",
                    "description": f"Increase budget to ${current_rate * 1.15:.0f} for faster timeline",
                    "terms": {**current_offer, "rate": current_rate * 1.15, "timeline": "1-2 weeks"}
                })
                
                # Lower budget option with reduced deliverables
                alternatives.append({
                    "type": "budget_decrease",
                    "description": f"Reduce to ${current_rate * 0.85:.0f} with fewer deliverables",
                    "terms": {**current_offer, "rate": current_rate * 0.85, "deliverables": ["Single post"]}
                })
            
            # Timeline alternatives
            alternatives.append({
                "type": "flexible_timeline",
                "description": "Offer flexible timeline for better rate",
                "terms": {**current_offer, "timeline": "Flexible", "rate": current_rate * 0.9}
            })
            
            # Package deal alternative
            alternatives.append({
                "type": "package_deal",
                "description": "Multi-campaign package deal",
                "terms": {
                    **current_offer, 
                    "package": "3 campaigns",
                    "total_value": current_rate * 2.5,
                    "timeline": "3 months"
                }
            })
            
            return alternatives[:3]  # Return top 3 alternatives
            
        except Exception as e:
            print(f"Error generating alternatives: {e}")
            return []
    
    def _calculate_success_rate(self, request: NegotiationRequest, agent_response: Dict) -> float:
        """Calculate estimated success rate based on negotiation factors"""
        try:
            base_rate = 60.0  # Base success rate
            
            # Adjust based on action type
            action = agent_response.get("action", "")
            if action == "accept":
                base_rate = 95.0
            elif action == "counter_offer":
                base_rate = 70.0
            elif action == "request_clarification":
                base_rate = 80.0
            elif action == "escalate":
                base_rate = 30.0
            
            # Adjust based on confidence score
            confidence = agent_response.get("confidence_score", 50.0)
            confidence_adjustment = (confidence - 50) * 0.4
            
            # Adjust based on creator response history
            conversation_history = request.conversation_history
            if len(conversation_history) > 5:
                base_rate *= 0.9  # Reduce for lengthy negotiations
            
            # Adjust based on budget alignment
            proposed_terms = agent_response.get("proposed_terms", {})
            brand_constraints = request.brand_constraints
            
            if proposed_terms.get("rate", 0) <= brand_constraints.get("max_budget", 0):
                base_rate += 15  # Boost if within budget
            
            final_rate = max(10.0, min(95.0, base_rate + confidence_adjustment))
            return round(final_rate, 1)
            
        except Exception as e:
            print(f"Error calculating success rate: {e}")
            return 50.0
    
    def _generate_next_steps(self, agent_response: Dict) -> List[str]:
        """Generate recommended next steps based on agent response"""
        action = agent_response.get("action", "")
        
        if action == "accept":
            return [
                "Prepare contract with agreed terms",
                "Send contract for creator signature",
                "Schedule project kickoff meeting"
            ]
        elif action == "counter_offer":
            return [
                "Send counter-offer to creator",
                "Wait for creator response (24-48 hours)",
                "Prepare for potential follow-up negotiation"
            ]
        elif action == "request_clarification":
            return [
                "Request specific clarifications from creator",
                "Wait for detailed response",
                "Continue negotiation once clarity is achieved"
            ]
        elif action == "escalate":
            return [
                "Escalate to senior team member",
                "Review negotiation strategy",
                "Consider alternative creators if needed"
            ]
        else:
            return [
                "Review negotiation status",
                "Determine next appropriate action",
                "Continue dialogue with creator"
            ]
    
    async def _initialize_negotiation_metrics(self, negotiation_id: str, request: NegotiationRequest) -> bool:
        """Initialize metrics tracking for a new negotiation"""
        try:
            metrics = NegotiationMetrics(
                negotiation_id=negotiation_id,
                total_exchanges=1,
                duration_hours=0.0,
                success_probability=75.0,
                avg_response_time_hours=0.0,
                sentiment_trend=[0.7],  # Starting neutral-positive
                key_sticking_points=[],
                resolution_prediction="pending"
            )
            
            metrics_key = f"negotiation_metrics:{negotiation_id}"
            await redis_client.set_async(metrics_key, metrics.dict(), ttl=86400 * 30)  # 30 days
            
            return True
            
        except Exception as e:
            print(f"Error initializing negotiation metrics: {e}")
            return False
    
    async def _update_negotiation_metrics(
        self, 
        negotiation_id: str, 
        request: NegotiationRequest, 
        response: NegotiationResponse
    ) -> bool:
        """Update negotiation metrics with new exchange"""
        try:
            metrics_key = f"negotiation_metrics:{negotiation_id}"
            metrics_data = await redis_client.get_async(metrics_key)
            
            if metrics_data:
                metrics = NegotiationMetrics(**metrics_data)
                
                # Update basic metrics
                metrics.total_exchanges += 1
                metrics.success_probability = response.estimated_success_rate
                
                # Update sentiment trend (simplified)
                current_sentiment = 0.8 if response.confidence_score > 70 else 0.5
                metrics.sentiment_trend.append(current_sentiment)
                
                # Identify sticking points
                if response.action in [NegotiationAction.ESCALATE, NegotiationAction.REQUEST_CLARIFICATION]:
                    if "budget" in response.message.lower():
                        metrics.key_sticking_points.append("budget")
                    if "timeline" in response.message.lower():
                        metrics.key_sticking_points.append("timeline")
                
                # Update prediction
                if response.action == NegotiationAction.ACCEPT:
                    metrics.resolution_prediction = "success"
                elif response.escalation_needed:
                    metrics.resolution_prediction = "escalation_needed"
                
                await redis_client.set_async(metrics_key, metrics.dict(), ttl=86400 * 30)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating negotiation metrics: {e}")
            return False
    
    async def _finalize_negotiation_metrics(self, negotiation_id: str, outcome: str, final_terms: Dict) -> bool:
        """Finalize metrics when negotiation ends"""
        try:
            metrics_key = f"negotiation_metrics:{negotiation_id}"
            metrics_data = await redis_client.get_async(metrics_key)
            
            if metrics_data:
                metrics = NegotiationMetrics(**metrics_data)
                metrics.resolution_prediction = outcome
                
                # Calculate final duration (simplified)
                metrics.duration_hours = metrics.total_exchanges * 2.0  # Estimate 2 hours per exchange
                
                await redis_client.set_async(metrics_key, metrics.dict(), ttl=86400 * 90)  # 90 days for completed
                return True
            
            return False
            
        except Exception as e:
            print(f"Error finalizing negotiation metrics: {e}")
            return False