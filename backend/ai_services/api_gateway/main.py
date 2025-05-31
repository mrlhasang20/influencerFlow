from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import httpx
import asyncio
import uvicorn

app = FastAPI(title="InfluencerFlow AI Gateway")

# Service URLs
SERVICES = {
    "creator_discovery": "http://localhost:8001",
    "ai_communication": "http://localhost:8002", 
    "contract_automation": "http://localhost:8003"
}

class CampaignCreateRequest(BaseModel):
    brand_name: str
    campaign_name: str
    target_audience: str
    budget_range: str
    timeline: str
    deliverables: List[str]
    campaign_goals: List[str]

class CampaignResponse(BaseModel):
    campaign_id: str
    recommended_creators: List[Dict]
    outreach_messages: List[Dict]
    status: str

@app.post("/api/v1/campaign/create-with-ai", response_model=CampaignResponse)
async def create_campaign_with_ai(request: CampaignCreateRequest):
    """Complete AI-powered campaign creation workflow"""
    try:
        campaign_id = f"CAMP_{request.brand_name}_{int(asyncio.get_event_loop().time())}"
        
        # Step 1: Find creators
        async with httpx.AsyncClient() as client:
            search_response = await client.post(
                f"{SERVICES['creator_discovery']}/search",
                json={"query": request.target_audience, "limit": 5},
                timeout=10.0
            )
            creators = search_response.json()
        
        # Step 2: Generate outreach for top 3 creators
        outreach_results = []
        async with httpx.AsyncClient() as client:
            for creator in creators[:3]:
                try:
                    outreach_response = await client.post(
                        f"{SERVICES['ai_communication']}/generate-outreach",
                        json={
                            "creator_profile": creator,
                            "campaign_brief": {
                                "brand_name": request.brand_name,
                                "campaign_name": request.campaign_name,
                                "goal": ", ".join(request.campaign_goals),
                                "budget_range": request.budget_range,
                                "timeline": request.timeline,
                                "deliverables": request.deliverables
                            }
                        },
                        timeout=15.0
                    )
                    outreach_results.append({
                        "creator_id": creator["id"],
                        "creator_name": creator["name"],
                        "outreach": outreach_response.json()
                    })
                except Exception as e:
                    print(f"Outreach generation failed for {creator.get('name')}: {e}")
        
        return CampaignResponse(
            campaign_id=campaign_id,
            recommended_creators=creators,
            outreach_messages=outreach_results,
            status="created"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Check health of all services"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                health_status[service_name] = "unreachable"
    
    return {"status": "ok", "services": health_status}

@app.get("/")
async def root():
    return {"message": "InfluencerFlow AI Gateway", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
