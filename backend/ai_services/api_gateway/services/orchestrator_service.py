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
            
            return {
                "campaign_id": campaign.id,
                "status": "created",
                "recommended_creators": creators,
                "outreach_messages": outreach_messages,
                "draft_contracts": contracts,
                "payment_plans": payment_plans
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create campaign: {str(e)}")
    
    async def _find_top_creators(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find top 3 creators matching campaign requirements"""
        # For demo, return mock data
        return [
            {
                "id": "creator_1",
                "name": "Top Fashion Influencer",
                "platform": "Instagram",
                "followers": 1000000,
                "engagement_rate": 3.5,
                "match_score": 0.95
            },
            {
                "id": "creator_2",
                "name": "Lifestyle Creator",
                "platform": "YouTube",
                "followers": 500000,
                "engagement_rate": 4.2,
                "match_score": 0.92
            },
            {
                "id": "creator_3",
                "name": "Beauty Expert",
                "platform": "Instagram",
                "followers": 750000,
                "engagement_rate": 3.8,
                "match_score": 0.89
            }
        ]
    
    async def _generate_outreach_messages(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized outreach messages for each creator"""
        messages = []
        for creator in creators:
            message = {
                "creator_id": creator["id"],
                "subject": f"Collaboration Opportunity: {campaign.campaign_name}",
                "message": f"Hi {creator['name']},\n\nWe love your content and would like to collaborate with you on our {campaign.campaign_name} campaign...",
                "status": "draft"
            }
            messages.append(message)
        return messages
    
    async def _create_draft_contracts(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create draft contracts for each creator"""
        contracts = []
        for creator in creators:
            contract = {
                "creator_id": creator["id"],
                "campaign_id": campaign.id,
                "terms": {
                    "deliverables": campaign.content_types,
                    "timeline": campaign.timeline,
                    "compensation": f"Based on {campaign.budget_range}"
                },
                "status": "draft"
            }
            contracts.append(contract)
        return contracts
    
    async def _setup_payment_milestones(self, campaign: CampaignORM, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Set up payment milestones for each creator"""
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

    async def get_campaign_workflow_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get the current status of the campaign workflow"""
        # For demo purposes, return mock data
        return {
            "recommended_creators": [
                {
                    "id": "creator_1",
                    "name": "Fashion Influencer",
                    "platform": "Instagram",
                    "followers": 1000000,
                    "engagement_rate": 3.5,
                    "match_score": 0.95
                },
                {
                    "id": "creator_2",
                    "name": "Lifestyle Creator",
                    "platform": "YouTube",
                    "followers": 500000,
                    "engagement_rate": 4.2,
                    "match_score": 0.92
                }
            ],
            "outreach_messages": [
                {
                    "creator_id": "creator_1",
                    "subject": "Collaboration Opportunity",
                    "status": "sent"
                },
                {
                    "creator_id": "creator_2",
                    "subject": "Campaign Partnership",
                    "status": "draft"
                }
            ],
            "draft_contracts": [
                {
                    "creator_id": "creator_1",
                    "status": "negotiating",
                    "payment_milestones": [
                        {"percentage": 30, "description": "Upon signing"},
                        {"percentage": 40, "description": "Content delivery"},
                        {"percentage": 30, "description": "Campaign completion"}
                    ]
                }
            ]
        }
