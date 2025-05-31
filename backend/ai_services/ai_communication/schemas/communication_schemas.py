from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    NEGOTIATION = "negotiation"
    CONTRACT_OFFER = "contract_offer"
    CONFIRMATION = "confirmation"
    REJECTION = "rejection"

class NegotiationAction(str, Enum):
    ACCEPT = "accept"
    COUNTER_OFFER = "counter_offer"
    REQUEST_CLARIFICATION = "request_clarification"
    ESCALATE = "escalate"
    REJECT = "reject"

class NegotiationStrategy(str, Enum):
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    ACCOMMODATING = "accommodating"
    COMPROMISING = "compromising"

class CommunicationTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"

# Request Schemas
class OutreachRequest(BaseModel):
    creator_profile: Dict[str, Any] = Field(..., description="Creator profile information")
    campaign_brief: Dict[str, Any] = Field(..., description="Campaign details")
    message_type: MessageType = Field(default=MessageType.INITIAL_OUTREACH)
    custom_instructions: Optional[str] = Field(default=None, max_length=500)
    tone: CommunicationTone = Field(default=CommunicationTone.PROFESSIONAL)
    include_voice: bool = Field(default=False, description="Generate voice version")
    language: str = Field(default="English", description="Message language")
    
    @validator('creator_profile')
    def validate_creator_profile(cls, v):
        required_fields = ['name', 'platform']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Creator profile missing required field: {field}')
        return v
    
    @validator('campaign_brief')
    def validate_campaign_brief(cls, v):
        required_fields = ['brand_name', 'campaign_name']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Campaign brief missing required field: {field}')
        return v

class NegotiationRequest(BaseModel):
    negotiation_id: Optional[str] = Field(default=None, description="Existing negotiation ID")
    creator_profile: Dict[str, Any] = Field(..., description="Creator profile")
    campaign_brief: Dict[str, Any] = Field(..., description="Campaign details")
    creator_response: Optional[Dict[str, Any]] = Field(default=None, description="Creator's response/proposal")
    brand_constraints: Dict[str, Any] = Field(..., description="Brand constraints and limits")
    strategy: NegotiationStrategy = Field(default=NegotiationStrategy.COLLABORATIVE)
    conversation_history: List[Dict[str, Any]] = Field(default=[], description="Previous conversation")

class ContentAnalysisRequest(BaseModel):
    content_samples: List[str] = Field(..., min_items=1, max_items=10, description="Content samples to analyze")
    analysis_type: str = Field(default="brand_safety", description="Type of analysis to perform")
    creator_id: Optional[str] = Field(default=None, description="Creator ID for context")
    
    @validator('content_samples')
    def validate_content_samples(cls, v):
        for content in v:
            if len(content.strip()) < 10:
                raise ValueError('Content samples must be at least 10 characters long')
        return v

class VoiceGenerationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")
    voice_id: str = Field(default="default", description="Voice ID to use")
    language: str = Field(default="en", description="Language code")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")

# Response Schemas
class OutreachResponse(BaseModel):
    message: str = Field(..., description="Generated outreach message")
    message_type: MessageType
    tone: CommunicationTone
    language: str
    word_count: int = Field(ge=0)
    estimated_read_time: float = Field(ge=0, description="Estimated read time in seconds")
    has_voice: bool = Field(default=False)
    voice_url: Optional[str] = Field(default=None)
    personalization_score: float = Field(ge=0, le=100, description="How personalized the message is")
    compliance_check: Dict[str, bool] = Field(default={}, description="Compliance checks passed")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class NegotiationResponse(BaseModel):
    negotiation_id: str = Field(..., description="Unique negotiation identifier")
    action: NegotiationAction = Field(..., description="Recommended action")
    message: str = Field(..., description="Response message to creator")
    proposed_terms: Dict[str, Any] = Field(default={}, description="Proposed deal terms")
    justification: str = Field(..., description="Reasoning behind the decision")
    confidence_score: float = Field(ge=0, le=100, description="Confidence in this approach")
    escalation_needed: bool = Field(default=False, description="Whether human intervention is needed")
    alternative_options: List[Dict[str, Any]] = Field(default=[], description="Alternative approaches")
    estimated_success_rate: float = Field(ge=0, le=100, description="Estimated success rate")
    next_steps: List[str] = Field(default=[], description="Recommended next steps")

class ContentAnalysisResponse(BaseModel):
    analysis_type: str
    creator_id: Optional[str] = None
    overall_score: float = Field(ge=0, le=100, description="Overall analysis score")
    
    # Brand Safety Analysis
    safety_score: Optional[float] = Field(default=None, ge=0, le=100)
    risk_factors: List[str] = Field(default=[])
    positive_indicators: List[str] = Field(default=[])
    
    # Content Insights
    content_themes: List[str] = Field(default=[])
    language_analysis: Dict[str, Any] = Field(default={})
    audience_insights: Dict[str, Any] = Field(default={})
    
    # Performance Prediction
    engagement_prediction: Optional[Dict[str, Any]] = Field(default=None)
    viral_potential: Optional[float] = Field(default=None, ge=0, le=100)
    
    recommendations: List[str] = Field(default=[])
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class VoiceGenerationResponse(BaseModel):
    audio_url: str = Field(..., description="URL to generated audio file")
    duration_seconds: float = Field(ge=0, description="Audio duration")
    file_size_bytes: int = Field(ge=0, description="File size")
    voice_id: str
    language: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Complex Schemas for Advanced Features
class ConversationContext(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    creator_id: str = Field(..., description="Creator identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    messages: List[Dict[str, Any]] = Field(default=[], description="Message history")
    current_status: str = Field(default="active", description="Conversation status")
    metadata: Dict[str, Any] = Field(default={}, description="Additional context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BatchOutreachRequest(BaseModel):
    creator_profiles: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50)
    campaign_brief: Dict[str, Any] = Field(..., description="Campaign details")
    message_type: MessageType = Field(default=MessageType.INITIAL_OUTREACH)
    personalization_level: str = Field(default="high", description="Level of personalization")
    batch_id: Optional[str] = Field(default=None, description="Batch identifier")

class BatchOutreachResponse(BaseModel):
    batch_id: str = Field(..., description="Batch identifier")
    total_creators: int = Field(ge=0)
    successful_generations: int = Field(ge=0)
    failed_generations: int = Field(ge=0)
    messages: List[Dict[str, Any]] = Field(default=[], description="Generated messages")
    processing_time_seconds: float = Field(ge=0)
    estimated_delivery_time: float = Field(ge=0, description="Estimated time to send all messages")

class NegotiationMetrics(BaseModel):
    negotiation_id: str
    total_exchanges: int = Field(ge=0)
    duration_hours: float = Field(ge=0)
    success_probability: float = Field(ge=0, le=100)
    avg_response_time_hours: float = Field(ge=0)
    sentiment_trend: List[float] = Field(default=[], description="Sentiment over time")
    key_sticking_points: List[str] = Field(default=[])
    resolution_prediction: str = Field(default="pending")

class CommunicationInsights(BaseModel):
    creator_id: str
    total_interactions: int = Field(ge=0)
    avg_response_time_hours: float = Field(ge=0)
    preferred_communication_style: str = Field(default="unknown")
    successful_campaigns: int = Field(ge=0)
    response_rate: float = Field(ge=0, le=100)
    sentiment_analysis: Dict[str, float] = Field(default={})
    best_outreach_times: List[str] = Field(default=[])
    language_preferences: List[str] = Field(default=["English"])

class AutomationSettings(BaseModel):
    auto_follow_up: bool = Field(default=False)
    follow_up_delay_hours: int = Field(default=24, ge=1, le=168)
    max_follow_ups: int = Field(default=2, ge=0, le=5)
    auto_negotiate: bool = Field(default=False)
    negotiation_boundaries: Dict[str, Any] = Field(default={})
    escalation_triggers: List[str] = Field(default=[])
    response_time_sla_hours: int = Field(default=24, ge=1, le=168)

# Health Check Schema
class CommunicationHealthCheck(BaseModel):
    service_status: str = "healthy"
    gemini_api_status: str = "connected"
    voice_service_status: str = "available"
    active_conversations: int = Field(ge=0)
    active_negotiations: int = Field(ge=0)
    messages_generated_today: int = Field(ge=0)
    avg_generation_time_ms: float = Field(ge=0)
    last_health_check: datetime = Field(default_factory=datetime.utcnow)

# Error Schemas
class CommunicationError(BaseModel):
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    creator_id: Optional[str] = None
    campaign_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    field: str
    message: str
    invalid_value: Optional[Any] = None
    suggestion: Optional[str] = None