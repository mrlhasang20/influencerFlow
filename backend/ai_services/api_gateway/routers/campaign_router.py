# Campaign workflow 

# backend/ai_services/api_gateway/routers/campaign_router.py
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import httpx
from sqlalchemy.orm import Session

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import shared modules
from shared.database import get_db, Campaign as CampaignORM
from shared.config import settings
from shared.database import Campaign, Creator

# Import local schemas
from schemas.campaign_schemas import CampaignCreate, CampaignResponse

# Import local services
from api_gateway.services.orchestrator_service import OrchestratorService

# Remove the prefix since it's added in main.py
router = APIRouter(tags=["campaigns"])
orchestrator = OrchestratorService()

@router.post("/")
async def create_campaign(campaign_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new campaign"""
    try:
        # Create the campaign in the database
        new_campaign = Campaign(**campaign_data)
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)

        # Start the AI workflow
        workflow_result = await orchestrator.create_complete_campaign(campaign_data, db)

        return {
            "id": new_campaign.id,
            "brand_name": new_campaign.brand_name,
            "campaign_name": new_campaign.campaign_name,
            "description": new_campaign.description,
            "status": new_campaign.status,
            "created_at": str(new_campaign.created_at),
            "workflow": workflow_result
        }
    except Exception as e:
        db.rollback()
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
        
        # Get AI workflow data
        workflow_data = await orchestrator.get_campaign_workflow_status(campaign_id)
        
        return {
            "id": campaign.id,  # Changed from campaign_id to id to match frontend
            "brand_name": campaign.brand_name,
            "campaign_name": campaign.campaign_name,
            "description": campaign.description,
            "target_audience": campaign.target_audience,
            "budget_range": campaign.budget_range,
            "timeline": campaign.timeline,
            "platforms": campaign.platforms,
            "content_types": campaign.content_types,
            "campaign_goals": campaign.campaign_goals,
            "status": campaign.status,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            # Add AI workflow data
            "recommended_creators": workflow_data.get("recommended_creators", []),
            "outreach_messages": workflow_data.get("outreach_messages", []),
            "draft_contracts": workflow_data.get("draft_contracts", []),
            "payment_plans": workflow_data.get("payment_plans", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns"""
    try:
        campaigns = db.query(CampaignORM).all()
        campaign_list = []
        
        for c in campaigns:
            if not c.id:  # Skip campaigns without IDs
                continue
                
            campaign_list.append({
                "id": str(c.id),  # Ensure ID is a string
                "brand_name": c.brand_name,
                "campaign_name": c.campaign_name,
                "description": c.description,
                "status": c.status,
                "created_at": str(c.created_at)
            })
            
        return {"campaigns": campaign_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    try:
        new_campaign = Campaign(**campaign.dict())
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        return new_campaign
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).all()

@router.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, campaign_update: CampaignCreate, db: Session = Depends(get_db)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    for key, value in campaign_update.dict().items():
        setattr(db_campaign, key, value)
    
    db.commit()
    return db_campaign

@router.post("/campaigns/complete", response_model=Dict[str, Any])
async def create_complete_campaign(campaign_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a complete campaign with AI-powered workflow"""
    try:
        result = await orchestrator.create_complete_campaign(campaign_data, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
