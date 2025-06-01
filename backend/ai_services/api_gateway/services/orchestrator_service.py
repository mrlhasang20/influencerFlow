# backend/ai_services/api_gateway/services/orchestrator_service.py
import sys
import httpx
import asyncio
from typing import Dict, Any
from pathlib import Path
import uuid
from sqlalchemy.orm import Session
from shared.database import get_db, Campaign as CampaignORM

sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings

class OrchestratorService:
    async def create_complete_campaign(self, campaign_data: Dict[str, Any], db: Session = None) -> Dict[str, Any]:
        """Orchestrate full campaign creation workflow"""
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Creator Discovery
                discovery_response = await client.post(
                    f"http://localhost:{settings.creator_discovery_port}/search",
                    json={"query": campaign_data["target_audience"], "limit": 10},
                    timeout=30.0
                )
                discovery_response.raise_for_status()
                
                print("Discovery response:", discovery_response.json())
                
                creators_response = discovery_response.json()
                if isinstance(creators_response, dict) and "results" in creators_response:
                    creators = creators_response["results"]
                elif isinstance(creators_response, list):
                    creators = creators_response
                else:
                    raise Exception(f"Creator discovery did not return a list: {creators_response}")
                
                # Step 2: Generate Outreach Messages
                outreach_tasks = []
                for creator in creators[:3]:  # Top 3 creators
                    print("CREATOR OBJECT:", creator)
                    print("Outreach payload:", {
                        "creator_profile": creator,
                        "campaign_brief": campaign_data
                    })
                    outreach_tasks.append(
                        client.post(
                            f"http://localhost:{settings.ai_communication_port}/generate-outreach",
                            json={
                                "creator_profile": creator,
                                "campaign_brief": campaign_data
                            },
                            timeout=30.0
                        )
                    )
                outreach_responses = await asyncio.gather(*outreach_tasks, return_exceptions=True)
                
                print("Outreach responses:", outreach_responses)
                for idx, r in enumerate(outreach_responses):
                    print(f"Response {idx}: type={type(r)}, status={getattr(r, 'status_code', None)}")
                    if hasattr(r, "text"):
                        print(f"Response {idx} text: {r.text}")
                
                # Step 3: Create Campaign Records
                campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
                new_campaign = CampaignORM(
                    id=campaign_id,
                    brand_name=campaign_data["brand_name"],
                    campaign_name=campaign_data["campaign_name"],
                    description=campaign_data.get("description", ""),
                    target_audience=campaign_data["target_audience"],
                    budget_range=campaign_data["budget_range"],
                    timeline=campaign_data["timeline"],
                    deliverables=campaign_data.get("deliverables", []),
                    status="draft",
                    created_by=campaign_data.get("created_by", "system")
                )
                db.add(new_campaign)
                db.commit()
                db.refresh(new_campaign)
                
                outreach_messages = []
                for r in outreach_responses:
                    if isinstance(r, Exception):
                        outreach_messages.append({"error": str(r)})
                    elif hasattr(r, "status_code") and r.status_code == 200:
                        try:
                            data = await r.json()
                            outreach_messages.append(data)
                        except Exception as e:
                            outreach_messages.append({"error": f"Failed to parse JSON: {str(e)}", "raw": getattr(r, "text", str(r))})
                    else:
                        outreach_messages.append({
                            "error": f"Outreach service returned status {getattr(r, 'status_code', 'unknown')}",
                            "text": getattr(r, 'text', str(r))
                        })
                
                result = {
                    "campaign_id": new_campaign.id,
                    "status": new_campaign.status,
                    "creators_discovered": len(creators),
                    "outreach_messages": outreach_messages,
                    "next_steps": ["negotiation", "contract_signing"]
                }
                print("FINAL RESULT:", result)
                return result
        except httpx.HTTPError as e:
            raise Exception(f"Service communication error: {str(e)}")
        except Exception as e:
            raise Exception(f"Campaign creation failed: {str(e)}")
