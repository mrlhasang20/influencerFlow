# Campaign workflow 

# backend/ai_services/api_gateway/routers/campaign_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import httpx
import sys
from pathlib import Path
from sqlalchemy.orm import Session
import uuid
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
from shared.database import get_db, Campaign, Collaboration, Contract

# Remove the prefix since it's added in main.py
router = APIRouter(tags=["campaigns"])
orchestrator = OrchestratorService()

@router.post("/")
async def create_campaign(campaign_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new campaign with AI-powered creator discovery and outreach"""
    try:
        # Create campaign record in database
        campaign = Campaign(
            id=campaign_data.get("campaign_id", f"camp_{uuid.uuid4().hex[:8]}"),
            brand_name=campaign_data["brand_name"],
            campaign_name=campaign_data["campaign_name"],
            description=campaign_data.get("description", ""),
            target_audience=campaign_data["target_audience"],
            budget_range=campaign_data["budget_range"],
            timeline=campaign_data["timeline"],
            deliverables=campaign_data.get("deliverables", []),
            status="created",
            created_by=campaign_data.get("created_by", "system")
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        # Run AI workflow
        result = await orchestrator.create_complete_campaign(campaign_data)
        
        # Update campaign with AI results
        campaign.status = result["status"]
        campaign.deliverables = result.get("deliverables", [])
        db.commit()
        db.refresh(campaign)

        return {
            **result,
            "campaign": {
                "id": campaign.id,
                "brand_name": campaign.brand_name,
                "campaign_name": campaign.campaign_name,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat()
            }
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
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get collaborations for this campaign
        collaborations = db.query(Collaboration).filter(
            Collaboration.campaign_id == campaign_id
        ).all()

        # Get contracts for this campaign
        contracts = []
        for collab in collaborations:
            if collab.contract_id:
                contract = db.query(Contract).filter(
                    Contract.id == collab.contract_id
                ).first()
                if contract:
                    contracts.append(contract)

        return {
            "campaign": {
                "id": campaign.id,
                "brand_name": campaign.brand_name,
                "campaign_name": campaign.campaign_name,
                "description": campaign.description,
                "target_audience": campaign.target_audience,
                "budget_range": campaign.budget_range,
                "timeline": campaign.timeline,
                "deliverables": campaign.deliverables,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat()
            },
            "collaborations": [
                {
                    "id": collab.id,
                    "creator_id": collab.creator_id,
                    "status": collab.status,
                    "outreach_message": collab.outreach_message,
                    "negotiation_history": collab.negotiation_history,
                    "final_terms": collab.final_terms,
                    "contract_id": collab.contract_id,
                    "created_at": collab.created_at.isoformat(),
                    "updated_at": collab.updated_at.isoformat()
                }
                for collab in collaborations
            ],
            "contracts": [
                {
                    "id": contract.id,
                    "collaboration_id": contract.collaboration_id,
                    "status": contract.status,
                    "terms": contract.terms,
                    "created_at": contract.created_at.isoformat(),
                    "signed_at": contract.signed_at.isoformat() if contract.signed_at else None
                }
                for contract in contracts
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_campaigns(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    status: str = None
):
    """List all campaigns with optional filtering"""
    try:
        query = db.query(Campaign)
        
        if status:
            query = query.filter(Campaign.status == status)
        
        total = query.count()
        campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "campaigns": [
                {
                    "id": campaign.id,
                    "brand_name": campaign.brand_name,
                    "campaign_name": campaign.campaign_name,
                    "status": campaign.status,
                    "created_at": campaign.created_at.isoformat(),
                    "updated_at": campaign.updated_at.isoformat(),
                    "creators_discovered": len(db.query(Collaboration).filter(
                        Collaboration.campaign_id == campaign.id
                    ).all())
                }
                for campaign in campaigns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
