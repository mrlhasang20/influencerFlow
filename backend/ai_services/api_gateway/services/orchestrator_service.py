# backend/ai_services/api_gateway/services/orchestrator_service.py
import sys
import httpx
import asyncio
from typing import Dict, Any, List
from pathlib import Path
import uuid
from sqlalchemy.orm import Session
from shared.database import get_db, Campaign as CampaignORM, Creator

sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings

class OrchestratorService:
    async def create_complete_campaign(self, campaign_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Orchestrate the complete campaign creation flow:
        1. Create campaign
        2. Find top creators
        3. Generate outreach messages
        4. Create contracts
        5. Set up payment milestones
        """
        try:
            # 1. Create campaign record
            campaign = CampaignORM(**campaign_data)
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            
            # 2. Find top creators based on campaign requirements
            creators = await self._find_top_creators(campaign_data)
            
            # 3. Generate personalized outreach for each creator
            outreach_messages = await self._generate_outreach_messages(campaign, creators)
            
            # 4. Create draft contracts
            contracts = await self._create_draft_contracts(campaign, creators)
            
            # 5. Set up payment milestones
            payment_plans = await self._setup_payment_milestones(campaign, creators)
            
            # Update campaign with workflow data
            campaign_dict = {
                "campaign_id": campaign.id,
                "status": "in_progress",
                "recommended_creators": creators,
                "outreach_messages": outreach_messages,
                "draft_contracts": contracts,
                "payment_plans": payment_plans
            }
            
            # Store workflow data in database
            campaign.workflow_data = campaign_dict
            db.commit()
            
            return campaign_dict
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create campaign: {str(e)}")
    
    async def _find_top_creators(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find top creators matching campaign requirements using AI"""
        try:
            # Make API call to creator discovery service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{settings.creator_discovery_port}/api/v1/creators/search",
                    json={
                        "campaign": campaign_data,
                        "filters": {
                            "platforms": campaign_data.get("platforms", []),
                            "min_followers": 1000,
                            "min_engagement_rate": 1.0,
                            "categories": campaign_data.get("content_types", [])
                        },
                        "limit": 3
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("creators", [])
                return []
        except Exception as e:
            print(f"Error finding creators: {e}")
            return []
    
    async def _generate_outreach_messages(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized outreach messages using AI"""
        try:
            # Prepare campaign brief
            campaign_brief = {
                "brand_name": campaign.brand_name,
                "campaign_name": campaign.campaign_name,
                "description": campaign.description,
                "target_audience": campaign.target_audience,
                "budget_range": campaign.budget_range,
                "timeline": campaign.timeline,
                "platforms": campaign.platforms,
                "content_types": campaign.content_types,
                "campaign_goals": campaign.campaign_goals
            }
            
            # Make API call to AI communication service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{settings.ai_communication_port}/api/v1/outreach/batch",
                    json={
                        "creator_profiles": creators,
                        "campaign_brief": campaign_brief,
                        "message_type": "initial_outreach",
                        "personalization_level": "high"
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("messages", [])
                return []
        except Exception as e:
            print(f"Error generating outreach: {e}")
            return []
    
    async def _create_draft_contracts(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create AI-generated draft contracts"""
        try:
            contracts = []
            for creator in creators:
                # Make API call to contract automation service
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"http://localhost:{settings.contract_automation_port}/api/v1/contracts/generate",
                            json={
                            "campaign_id": campaign.id,
                            "creator": creator,
                            "terms": {
                                "deliverables": campaign.content_types,
                                "timeline": campaign.timeline,
                                "compensation": campaign.budget_range,
                                "platforms": campaign.platforms
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        contracts.append(response.json())
            return contracts
        except Exception as e:
            print(f"Error creating contracts: {e}")
            return []
    
    async def _setup_payment_milestones(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Set up payment milestones for each creator"""
        try:
            payment_plans = []
            for creator in creators:
                plan = {
                    "creator_id": creator["id"],
                    "campaign_id": campaign.id,
                    "milestones": [
                        {"percentage": 30, "description": "Upon contract signing"},
                        {"percentage": 40, "description": "Upon content submission"},
                        {"percentage": 30, "description": "Upon campaign completion"}
                    ],
                    "status": "draft"
                }
                payment_plans.append(plan)
            return payment_plans
        except Exception as e:
            print(f"Error setting up payments: {e}")
            return []

    async def get_campaign_workflow_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get the current status of the campaign workflow"""
        try:
            if not campaign_id:
                raise ValueError("Campaign ID is required")
            
            # Get campaign from database
            db = next(get_db())
            campaign = db.query(CampaignORM).filter(CampaignORM.id == campaign_id).first()
            
            if not campaign:
                return {
                    "recommended_creators": [],
                    "outreach_messages": [],
                    "draft_contracts": [],
                    "payment_plans": []
                }
            
            # Return workflow data if it exists
            return campaign.workflow_data or {
                "recommended_creators": [],
                "outreach_messages": [],
                "draft_contracts": [],
                "payment_plans": []
            }
            
        except Exception as e:
            print(f"Error in get_campaign_workflow_status: {str(e)}")
            return {
                "recommended_creators": [],
                "outreach_messages": [],
                "draft_contracts": [],
                "payment_plans": []
            }
