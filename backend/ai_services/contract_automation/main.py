# backend/ai_services/contract_automation/main.py

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any
import uvicorn
from services.contract_service import ContractService
from services.legal_service import LegalService
from schemas.contract_schemas import (
    ContractGenerationRequest, ContractResponse, 
    ComplianceCheckRequest, ComplianceResponse,
    ContractTemplateRequest, TemplateResponse
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.config import settings

app = FastAPI(
    title="Contract Automation Service", 
    version="1.0.0",
    description="AI-powered contract generation and legal compliance"
)

# Initialize services
contract_service = ContractService()
legal_service = LegalService()

@app.post("/generate-contract", response_model=ContractResponse)
async def generate_contract(request: ContractGenerationRequest):
    """Generate AI-powered contract from negotiated terms"""
    try:
        contract_data = await contract_service.generate_contract(request.deal_terms)
        return ContractResponse(
            contract_id=contract_data["contract_id"],
            contract_text=contract_data["contract_text"],
            contract_html=contract_data.get("contract_html"),
            generated_at=contract_data["generated_at"],
            status="generated",
            metadata=contract_data.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract generation failed: {str(e)}")

@app.post("/check-compliance", response_model=ComplianceResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """Check contract compliance with legal requirements"""
    try:
        compliance_result = await legal_service.check_compliance(
            request.contract_text, 
            request.jurisdiction,
            request.contract_type
        )
        return ComplianceResponse(
            is_compliant=compliance_result["is_compliant"],
            compliance_score=compliance_result["compliance_score"],
            issues=compliance_result["issues"],
            recommendations=compliance_result["recommendations"],
            required_clauses=compliance_result.get("required_clauses", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")

@app.get("/templates", response_model=List[TemplateResponse])
async def get_contract_templates():
    """Get available contract templates"""
    try:
        templates = await contract_service.get_available_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")

@app.post("/customize-template", response_model=ContractResponse)
async def customize_template(request: ContractTemplateRequest):
    """Customize contract template with specific terms"""
    try:
        customized_contract = await contract_service.customize_template(
            request.template_id,
            request.customization_data
        )
        return customized_contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template customization failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "contract-automation"}

@app.get("/debug/contract-preview")
async def debug_contract_preview():
    """Debug endpoint for contract preview"""
    mock_terms = {
        "brand_name": "TechCorp Inc.",
        "influencer_name": "JaneFitness",
        "platform": "Instagram",
        "campaign_name": "Summer Fitness Challenge",
        "total_fee": 2500,
        "deliverables": [
            {"type": "Instagram Post", "quantity": 3, "due_date": "2024-07-15"},
            {"type": "Instagram Story", "quantity": 5, "due_date": "2024-07-10"}
        ],
        "start_date": "2024-07-01",
        "end_date": "2024-07-31",
        "payment_schedule": [
            {"milestone": "Contract Signing", "amount": 1250, "due_date": "2024-07-01"},
            {"milestone": "Campaign Completion", "amount": 1250, "due_date": "2024-08-05"}
        ]
    }
    
    try:
        contract_data = await contract_service.generate_contract(mock_terms)
        return {
            "preview": contract_data["contract_text"][:500] + "...",
            "contract_id": contract_data["contract_id"],
            "status": "demo_generated"
        }
    except Exception as e:
        return {"error": str(e), "status": "demo_failed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.contract_automation_port)
