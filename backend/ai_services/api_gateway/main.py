from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Dict, List, Any
import uvicorn
from routers.ai_router import router as ai_router
from routers.campaign_router import router as campaign_router
from middleware.cors_middleware import setup_cors
from services.orchestrator_service import OrchestratorService
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.config import settings

app = FastAPI(
    title="InfluencerFlow API Gateway",
    version="1.0.0",
    description="Unified API gateway for InfluencerFlow AI services"
)

# Setup CORS
setup_cors(app)

# Initialize orchestrator
orchestrator = OrchestratorService()

# Include routers with correct prefixes
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Services"])
app.include_router(campaign_router, prefix="/api/v1/campaigns", tags=["Campaigns"])

# Service URLs mapping
SERVICES = {
    "creator_discovery": f"http://localhost:{settings.creator_discovery_port}",
    "ai_communication": f"http://localhost:{settings.ai_communication_port}",
    "contract_automation": f"http://localhost:{settings.contract_automation_port}",
    "analytics_engine": f"http://localhost:{settings.analytics_engine_port}"
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "InfluencerFlow API Gateway",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "available_services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services"""
    health_status = {"gateway": "healthy", "services": {}}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health")
                health_status["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
                }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    # Determine overall health
    unhealthy_services = [name for name, status in health_status["services"].items() 
                         if status["status"] != "healthy"]
    
    overall_status = "healthy" if not unhealthy_services else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": asyncio.get_event_loop().time(),
        "details": health_status,
        "unhealthy_services": unhealthy_services
    }

@app.post("/api/v1/campaign/create-with-ai")
async def create_campaign_with_ai(campaign_data: Dict[str, Any]):
    """Complete AI-powered campaign creation workflow"""
    try:
        result = await orchestrator.create_complete_campaign(campaign_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")

@app.post("/api/v1/demo/quick-campaign")
async def quick_demo_campaign():
    """Quick demo campaign creation for testing"""
    demo_data = {
        "brand_name": "FitLife Co.",
        "campaign_name": "Summer Fitness Challenge",
        "target_audience": "fitness enthusiasts aged 18-35",
        "budget_range": "$2000-5000",
        "timeline": "30 days",
        "platforms": ["Instagram", "YouTube"],
        "content_types": ["posts", "stories", "videos"],
        "campaign_goals": ["brand_awareness", "product_promotion", "engagement"]
    }
    
    try:
        result = await orchestrator.create_complete_campaign(demo_data)
        return {
            "demo": True,
            "message": "Demo campaign created successfully",
            "campaign_data": result
        }
    except Exception as e:
        return {
            "demo": True,
            "error": str(e),
            "fallback_data": {
                "campaign_id": "demo_campaign_001",
                "status": "created",
                "recommended_creators": 3,
                "estimated_reach": 500000
            }
        }

@app.get("/api/v1/services/status")
async def get_services_status():
    """Get detailed status of all AI services"""
    status_data = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICES.items():
            try:
                # Try to get more detailed status if available
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    status_data[service_name] = {
                        "status": "online",
                        "url": service_url,
                        "response_data": response.json()
                    }
                else:
                    status_data[service_name] = {
                        "status": "error",
                        "url": service_url,
                        "status_code": response.status_code
                    }
            except Exception as e:
                status_data[service_name] = {
                    "status": "offline",
                    "url": service_url,
                    "error": str(e)
                }
    
    return status_data

# Error handlers
@app.exception_handler(httpx.RequestError)
async def http_error_handler(request, exc):
    return HTTPException(
        status_code=503,
        detail=f"Service communication error: {str(exc)}"
    )

@app.exception_handler(httpx.TimeoutException)
async def timeout_error_handler(request, exc):
    return HTTPException(
        status_code=504,
        detail="Service request timeout"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.api_gateway_port)