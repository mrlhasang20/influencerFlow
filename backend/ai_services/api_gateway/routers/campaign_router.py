# Campaign workflow 

# backend/ai_services/api_gateway/routers/campaign_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import httpx
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api_gateway.services.orchestrator_service import OrchestratorService
from shared.config import settings

# Remove the prefix since it's added in main.py
router = APIRouter(tags=["campaigns"])
orchestrator = OrchestratorService()

@router.post("/")
async def create_campaign(campaign_data: Dict[str, Any]):
    """Create a new campaign with AI-powered creator discovery and outreach"""
    try:
        result = await orchestrator.create_complete_campaign(campaign_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/demo")
async def create_demo_campaign():
    """Create a demo campaign for testing"""
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

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details by ID"""
    try:
        # TODO: Implement campaign retrieval
        return {"campaign_id": campaign_id, "status": "retrieved"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Campaign not found: {str(e)}")

@router.get("/")
async def list_campaigns():
    """List all campaigns"""
    try:
        # TODO: Implement campaign listing
        return {"campaigns": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
