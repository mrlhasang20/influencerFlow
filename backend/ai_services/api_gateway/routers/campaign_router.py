# Campaign workflow 

# backend/ai_services/api_gateway/routers/campaign_router.py
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import httpx
from sqlalchemy.orm import Session

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import shared modules
from shared.database import get_db, Campaign as CampaignORM
from shared.config import settings

# Import local schemas
from schemas.campaign_schemas import CampaignCreate, CampaignResponse

# Import local services
from api_gateway.services.orchestrator_service import OrchestratorService

# Remove the prefix since it's added in main.py
router = APIRouter(tags=["campaigns"])
orchestrator = OrchestratorService()

@router.post("/")
async def create_campaign(campaign_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new campaign with AI-powered creator discovery and outreach"""
    try:
        result = await orchestrator.create_complete_campaign(campaign_data, db)
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
async def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Get campaign details by ID"""
    try:
        campaign = db.query(CampaignORM).filter(CampaignORM.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {
            "campaign_id": campaign.id,
            "brand_name": campaign.brand_name,
            "campaign_name": campaign.campaign_name,
            "description": campaign.description,
            "target_audience": campaign.target_audience,
            "budget_range": campaign.budget_range,
            "timeline": campaign.timeline,
            "deliverables": campaign.deliverables,
            "status": campaign.status,
            "created_by": campaign.created_by,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns"""
    try:
        campaigns = db.query(CampaignORM).all()
        return {
            "campaigns": [
                {
                    "campaign_id": c.id,
                    "brand_name": c.brand_name,
                    "campaign_name": c.campaign_name,
                    "status": c.status,
                    "created_at": c.created_at
                }
                for c in campaigns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns")
async def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    # Create campaign in database
    campaign = Campaign(**campaign_data.dict())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign
