from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import asyncio
import json
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title="Contract Automation Service")

class ContractRequest(BaseModel):
    deal_terms: Dict
    template_type: str = "standard"

class ContractResponse(BaseModel):
    contract_text: str
    contract_id: str
    generated_at: datetime

@app.post("/generate-contract", response_model=ContractResponse)
async def generate_contract(request: ContractRequest):
    """Generate contract from deal terms"""
    
    terms = request.deal_terms
    contract_id = f"CONTRACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    contract_template = f'''
INFLUENCER MARKETING AGREEMENT
Contract ID: {contract_id}
Generated: {datetime.now().strftime('%B %d, %Y')}

PARTIES:
Brand: {terms.get('brand_name', 'Brand Name')}
Influencer: {terms.get('influencer_name', 'Influencer Name')}
Platform: {terms.get('platform', 'Social Media Platform')}

CAMPAIGN DETAILS:
Campaign Name: {terms.get('campaign_name', 'Marketing Campaign')}
Start Date: {terms.get('start_date', (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))}
End Date: {terms.get('end_date', (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%d'))}

DELIVERABLES:
{chr(10).join([f"- {deliverable}" for deliverable in terms.get('deliverables', ['1 Instagram post', '1 Instagram story'])])}

COMPENSATION:
Total Payment: ${terms.get('total_fee', 500)}
Payment Schedule: {terms.get('payment_schedule', 'Net 30 days after deliverable approval')}

TERMS & CONDITIONS:
1. Content Approval: All content must be approved by Brand before posting
2. FTC Compliance: Influencer must include proper disclosure (#ad, #sponsored, #partnership)
3. Usage Rights: Brand receives non-exclusive rights to repost content for 12 months
4. Exclusivity: Influencer agrees not to promote competing brands for 30 days
5. Performance: Influencer agrees to maintain content live for minimum 30 days

CANCELLATION:
Either party may cancel with 48 hours written notice before campaign start date.

By proceeding with this campaign, both parties agree to these terms.

Generated via InfluencerFlow AI Platform
'''

    return ContractResponse(
        contract_text=contract_template,
        contract_id=contract_id,
        generated_at=datetime.now()
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "contract-automation"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
