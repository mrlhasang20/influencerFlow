import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))



from services.outreach_service import OutreachService
from services.negotiation_service import NegotiationService
from services.voice_service import VoiceService
from schemas.communication_schemas import (
    # Request schemas
    OutreachRequest, NegotiationRequest, ContentAnalysisRequest,
    VoiceGenerationRequest, BatchOutreachRequest,
    
    # Response schemas
    OutreachResponse, NegotiationResponse, ContentAnalysisResponse,
    VoiceGenerationResponse, BatchOutreachResponse,
    CommunicationHealthCheck, NegotiationMetrics,
    
    # Enums
    MessageType, NegotiationAction, CommunicationTone
)
from shared.config import settings
from shared.utils import Timer, generate_id
from shared.redis_client import redis_client

# Global service instances
outreach_service = OutreachService()
negotiation_service = NegotiationService()
voice_service = VoiceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting AI Communication Service...")
    try:
        # Initialize services
        print("✅ AI Communication Service started successfully")
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down AI Communication Service...")

# FastAPI app with lifespan
app = FastAPI(
    title="AI Communication Service",
    description="AI-powered communication automation for influencer marketing using Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=CommunicationHealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_connected = redis_client.exists("test_key") is not None
        
        # Count active conversations and negotiations (simplified)
        active_conversations = 0
        active_negotiations = 0
        
        return CommunicationHealthCheck(
            service_status="healthy",
            gemini_api_status="connected" if settings.google_api_key else "not_configured",
            voice_service_status="available",
            active_conversations=active_conversations,
            active_negotiations=active_negotiations,
            messages_generated_today=123,  # Would be from analytics
            avg_generation_time_ms=450.0
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Outreach endpoints
@app.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach_message(request: OutreachRequest):
    """Generate personalized outreach message"""
    try:
        with Timer(f"Outreach generation API - {request.message_type}"):
            result = await outreach_service.generate_outreach_message(request)
            return result
    except Exception as e:
        print(f"Outreach generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")

@app.post("/outreach/batch", response_model=BatchOutreachResponse)
async def generate_batch_outreach(request: BatchOutreachRequest):
    """Generate outreach messages for multiple creators"""
    try:
        result = await outreach_service.generate_batch_outreach(request)
        return result
    except Exception as e:
        print(f"Batch outreach error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch outreach failed: {str(e)}")

@app.get("/outreach/suggestions")
async def get_message_suggestions(
    creator_id: str,
    campaign_id: str
):
    """Get message customization suggestions"""
    try:
        # This would load creator and campaign data
        creator_profile = {"name": "Creator", "platform": "Instagram"}  # Mock data
        campaign_brief = {"brand_name": "Brand", "campaign_name": "Campaign"}  # Mock data
        
        suggestions = await outreach_service.get_message_suggestions(creator_profile, campaign_brief)
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")

# Negotiation endpoints
@app.post("/negotiation/start", response_model=NegotiationResponse)
async def start_negotiation(request: NegotiationRequest):
    """Start a new negotiation process"""
    try:
        result = await negotiation_service.start_negotiation(request)
        return result
    except Exception as e:
        print(f"Negotiation start error: {e}")
        raise HTTPException(status_code=500, detail=f"Negotiation start failed: {str(e)}")

@app.post("/negotiation/respond", response_model=NegotiationResponse)
async def process_negotiation_response(request: NegotiationRequest):
    """Process creator response in ongoing negotiation"""
    try:
        result = await negotiation_service.process_negotiation_response(request)
        return result
    except Exception as e:
        print(f"Negotiation response error: {e}")
        raise HTTPException(status_code=500, detail=f"Negotiation response failed: {str(e)}")

@app.get("/negotiation/{negotiation_id}/status")
async def get_negotiation_status(negotiation_id: str):
    """Get current status of a negotiation"""
    try:
        status = await negotiation_service.get_negotiation_status(negotiation_id)
        return status
    except Exception as e:
        print(f"Negotiation status error: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.get("/negotiation/{negotiation_id}/history")
async def get_negotiation_history(negotiation_id: str):
    """Get conversation history for a negotiation"""
    try:
        history = await negotiation_service.get_negotiation_history(negotiation_id)
        return {"negotiation_id": negotiation_id, "history": history}
    except Exception as e:
        print(f"Negotiation history error: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@app.get("/negotiation/{negotiation_id}/metrics", response_model=NegotiationMetrics)
async def get_negotiation_metrics(negotiation_id: str):
    """Get metrics for a specific negotiation"""
    try:
        metrics = await negotiation_service.get_negotiation_metrics(negotiation_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Negotiation metrics not found")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        print(f"Negotiation metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@app.post("/negotiation/{negotiation_id}/end")
async def end_negotiation(
    negotiation_id: str,
    final_terms: Dict[str, Any],
    outcome: str
):
    """End a negotiation with final terms"""
    try:
        success = await negotiation_service.end_negotiation(negotiation_id, final_terms, outcome)
        return {"negotiation_id": negotiation_id, "ended": success, "outcome": outcome}
    except Exception as e:
        print(f"End negotiation error: {e}")
        raise HTTPException(status_code=500, detail=f"End negotiation failed: {str(e)}")

# Voice generation endpoints
@app.post("/voice/generate", response_model=VoiceGenerationResponse)
async def generate_voice(request: VoiceGenerationRequest):
    """Generate voice audio from text"""
    try:
        result = await voice_service.generate_voice(request)
        return result
    except Exception as e:
        print(f"Voice generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")

@app.get("/voice/voices")
async def get_available_voices(language: str = "en"):
    """Get list of available voices"""
    try:
        voices = await voice_service.get_available_voices(language)
        return {"language": language, "voices": voices}
    except Exception as e:
        print(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=f"Get voices failed: {str(e)}")

@app.post("/voice/outreach", response_model=VoiceGenerationResponse)
async def convert_outreach_to_voice(
    outreach_message: str,
    creator_profile: Dict[str, Any],
    voice_preferences: Optional[Dict[str, Any]] = None
):
    """Convert outreach message to voice"""
    try:
        result = await voice_service.convert_outreach_to_voice(
            outreach_message, creator_profile, voice_preferences
        )
        return result
    except Exception as e:
        print(f"Outreach voice conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice conversion failed: {str(e)}")

@app.post("/voice/batch")
async def batch_voice_generation(
    messages: List[Dict[str, str]],
    voice_settings: Dict[str, Any]
):
    """Generate voice for multiple messages"""
    try:
        results = await voice_service.batch_voice_generation(messages, voice_settings)
        return {"total_messages": len(messages), "successful_generations": len(results), "results": results}
    except Exception as e:
        print(f"Batch voice generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch voice generation failed: {str(e)}")

# Content analysis endpoints
@app.post("/analysis/content", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """Analyze creator content for brand safety and insights"""
    try:
        # Use Gemini client for content analysis
        from .models.gemini_client import GeminiAIClient
        
        gemini_client = GeminiAIClient()
        analysis_result = await gemini_client.analyze_creator_content(
            content_samples=request.content_samples,
            analysis_type=request.analysis_type
        )
        
        # Convert to response format
        response = ContentAnalysisResponse(
            analysis_type=request.analysis_type,
            creator_id=request.creator_id,
            overall_score=analysis_result.get("overall_score", 75.0),
            safety_score=analysis_result.get("safety_score"),
            risk_factors=analysis_result.get("risk_factors", []),
            positive_indicators=analysis_result.get("positive_indicators", []),
            content_themes=analysis_result.get("content_themes", []),
            language_analysis=analysis_result.get("language_analysis", {}),
            audience_insights=analysis_result.get("audience_insights", {}),
            recommendations=analysis_result.get("recommendations", [])
        )
        
        return response
    except Exception as e:
        print(f"Content analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Content analysis failed: {str(e)}")

# Utility endpoints
@app.post("/utils/validate-text")
async def validate_text_for_voice(text: str):
    """Validate text for voice generation"""
    try:
        validation_results = voice_service.validate_text_for_voice(text)
        return {"text": text[:50] + "..." if len(text) > 50 else text, "validation": validation_results}
    except Exception as e:
        print(f"Text validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Text validation failed: {str(e)}")

@app.get("/analytics/voice/{voice_id}")
async def get_voice_analytics(voice_id: str, days: int = 7):
    """Get analytics for voice usage"""
    try:
        analytics = await voice_service.get_voice_analytics(voice_id, days)
        return analytics
    except Exception as e:
        print(f"Voice analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice analytics failed: {str(e)}")

# Debug endpoints
@app.get("/debug/test-gemini")
async def debug_test_gemini():
    """Debug endpoint to test Gemini API connection"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Debug endpoint not available")
    
    try:
        from .models.gemini_client import GeminiAIClient
        
        gemini_client = GeminiAIClient()
        
        # Test basic message generation
        test_creator = {
            "name": "Test Creator",
            "platform": "Instagram",
            "content_style": "fitness and wellness content"
        }
        
        test_campaign = {
            "brand_name": "TestBrand",
            "campaign_name": "Test Campaign",
            "goal": "Brand awareness"
        }
        
        message = await gemini_client.generate_outreach_message(
            creator_profile=test_creator,
            campaign_brief=test_campaign,
            message_type="initial_outreach"
        )
        
        return {
            "gemini_status": "working",
            "test_message_length": len(message),
            "test_message_preview": message[:100] + "..." if len(message) > 100 else message
        }
    except Exception as e:
        return {"gemini_status": "error", "error": str(e)}

@app.post("/debug/test-workflow")
async def debug_test_workflow():
    """Debug endpoint to test complete communication workflow"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Debug endpoint not available")
    
    try:
        # Test outreach generation
        test_request = OutreachRequest(
            creator_profile={
                "name": "Test Creator",
                "platform": "Instagram",
                "content_style": "lifestyle and travel content",
                "categories": ["travel", "lifestyle"]
            },
            campaign_brief={
                "brand_name": "TestBrand",
                "campaign_name": "Summer Campaign",
                "goal": "Brand awareness",
                "target_audience": "young adults"
            }
        )
        
        outreach_result = await outreach_service.generate_outreach_message(test_request)
        
        return {
            "workflow_status": "success",
            "outreach_generated": True,
            "message_length": outreach_result.word_count,
            "personalization_score": outreach_result.personalization_score
        }
    except Exception as e:
        return {"workflow_status": "error", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.ai_communication_port,
        reload=settings.debug,
        log_level="info"
    )
