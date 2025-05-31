# AI service routes

from fastapi import APIRouter, HTTPException
import httpx
from typing import Dict, Any, List
import asyncio

router = APIRouter()

# Service endpoints
CREATOR_DISCOVERY_URL = "http://localhost:8001"
AI_COMMUNICATION_URL = "http://localhost:8002"
CONTRACT_AUTOMATION_URL = "http://localhost:8003"
ANALYTICS_ENGINE_URL = "http://localhost:8004"

@router.post("/creators/search")
async def search_creators(search_request: Dict[str, Any]):
    """Proxy to creator discovery service"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{CREATOR_DISCOVERY_URL}/search",
                json=search_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Creator discovery service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/communication/generate-outreach")
async def generate_outreach(outreach_request: Dict[str, Any]):
    """Proxy to AI communication service for outreach generation"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{AI_COMMUNICATION_URL}/generate-outreach",
                json=outreach_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"AI communication service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/negotiation/start")
async def start_negotiation(negotiation_request: Dict[str, Any]):
    """Proxy to AI communication service for starting negotiation"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{AI_COMMUNICATION_URL}/negotiation/start",
                json=negotiation_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"AI communication service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/negotiation/respond")
async def respond_negotiation(negotiation_request: Dict[str, Any]):
    """Proxy to AI communication service for responding to negotiation"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{AI_COMMUNICATION_URL}/negotiation/respond",
                json=negotiation_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"AI communication service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/generate-contract")
async def generate_contract(contract_request: Dict[str, Any]):
    """Proxy to contract automation service"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{CONTRACT_AUTOMATION_URL}/generate-contract",
                json=contract_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Contract automation service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/analytics/analyze-campaign")
async def analyze_campaign(analytics_request: Dict[str, Any]):
    """Proxy to analytics engine service"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ANALYTICS_ENGINE_URL}/analyze-campaign",
                json=analytics_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Analytics engine service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post("/analytics/predict-performance")
async def predict_performance(prediction_request: Dict[str, Any]):
    """Proxy to analytics engine for performance prediction"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ANALYTICS_ENGINE_URL}/predict-performance",
                json=prediction_request
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Analytics engine service error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/debug/test-all-services")
async def test_all_services():
    """Test all AI services with sample data"""
    results = {}
    
    # Test creator discovery
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{CREATOR_DISCOVERY_URL}/search",
                json={"query": "fitness influencers", "limit": 5}
            )
            results["creator_discovery"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        results["creator_discovery"] = {"status": "error", "error": str(e)}
    
    # Test AI communication
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AI_COMMUNICATION_URL}/generate-outreach",
                json={
                    "creator_profile": {"name": "TestCreator", "platform": "Instagram"},
                    "campaign_brief": {"brand_name": "TestBrand", "goal": "awareness"},
                    "message_type": "initial_outreach"
                }
            )
            results["ai_communication"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        results["ai_communication"] = {"status": "error", "error": str(e)}
    
    # Test contract automation
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{CONTRACT_AUTOMATION_URL}/debug/contract-preview")
            results["contract_automation"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        results["contract_automation"] = {"status": "error", "error": str(e)}
    
    # Test analytics engine
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ANALYTICS_ENGINE_URL}/debug/sample-analysis")
            results["analytics_engine"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        results["analytics_engine"] = {"status": "error", "error": str(e)}
    
    return {"test_results": results}