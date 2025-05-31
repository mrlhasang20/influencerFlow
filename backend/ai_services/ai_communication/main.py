from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import uvicorn
from pathlib import Path

# Get the parent directory path (ai_services)
parent_dir = Path(__file__).parent.parent
# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=parent_dir / ".env")

# Debug: Print the API key (first few characters for security)
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key starts with: {api_key[:8]}...")

app = FastAPI(title="AI Communication Service")

# Initialize OpenAI client
client = AsyncOpenAI(api_key=api_key)

class OutreachRequest(BaseModel):
    creator_profile: Dict
    campaign_brief: Dict
    message_type: str = "initial_outreach"

class OutreachResponse(BaseModel):
    message: str
    subject: str
    personalization_score: float

class NegotiationRequest(BaseModel):
    conversation_history: List[Dict]
    creator_proposal: Dict
    brand_constraints: Dict

class NegotiationResponse(BaseModel):
    action: str  # "accept", "counter", "reject"
    message: str
    proposed_terms: Optional[Dict] = None

@app.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach_message(request: OutreachRequest):
    """Generate personalized outreach message"""
    try:
        # Debug: Check if we're using OpenAI or template
        if not api_key:
            print("No API key found, using template")
            return await generate_template_outreach(request)
            
        print("Attempting to use OpenAI API...")
        system_prompt = '''You are an expert influencer marketing specialist. Create professional, 
        personalized outreach messages that are engaging and respectful. The message should:
        1. Address the creator by name
        2. Reference their specific content/platform
        3. Clearly explain the collaboration opportunity
        4. Be concise but comprehensive
        5. Include a clear call-to-action'''
        
        user_prompt = f'''
        Create an {request.message_type} message for:
        
        Creator: {request.creator_profile.get('name')}
        Platform: {request.creator_profile.get('platform')}
        Followers: {request.creator_profile.get('followers', 0):,}
        Content: {request.creator_profile.get('description')}
        
        Campaign:
        Brand: {request.campaign_brief.get('brand_name', 'Our Brand')}
        Product: {request.campaign_brief.get('product_name', 'Our Product')}
        Goal: {request.campaign_brief.get('goal', 'Increase brand awareness')}
        Budget: {request.campaign_brief.get('budget_range', '$500-1000')}
        Timeline: {request.campaign_brief.get('timeline', '2 weeks')}
        '''
        
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            message = response.choices[0].message.content
            subject = f"Collaboration Opportunity with {request.campaign_brief.get('brand_name', 'Our Brand')}"
            
            return OutreachResponse(
                message=message,
                subject=subject,
                personalization_score=0.8
            )
        except Exception as e:
            print(f"OpenAI API call failed: {str(e)}")
            return await generate_template_outreach(request)
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return await generate_template_outreach(request)

async def generate_template_outreach(request: OutreachRequest):
    """Fallback template-based message generation"""
    creator = request.creator_profile
    campaign = request.campaign_brief
    
    template_message = f'''Hi {creator.get('name', 'there')}!

I've been following your {creator.get('platform', 'content')} and really love your {', '.join(creator.get('categories', ['content'])[:2])} posts! Your {creator.get('description', 'content')} really resonates with our target audience.

We'd love to partner with you on an exciting campaign for {campaign.get('brand_name', 'our brand')}. Here's what we have in mind:

📍 Campaign: {campaign.get('goal', 'Brand awareness campaign')}
💰 Budget: {campaign.get('budget_range', '$500-1000')}
⏰ Timeline: {campaign.get('timeline', '2 weeks')}
📦 What we're looking for: {', '.join(campaign.get('deliverables', ['1 post', '1 story']))}

We believe your authentic voice and engaged community of {creator.get('followers', 0):,} followers would be perfect for this collaboration.

Would you be interested in learning more? I'd be happy to send over more details and discuss how we can make this work for both of us!

Looking forward to hearing from you!

Best regards,
[Your Name]
{campaign.get('brand_name', 'Brand')} Marketing Team'''

    return OutreachResponse(
        message=template_message,
        subject=f"Partnership Opportunity with {campaign.get('brand_name', 'Our Brand')}",
        personalization_score=0.6
    )

@app.post("/negotiate", response_model=NegotiationResponse)
async def handle_negotiation(request: NegotiationRequest):
    """Handle basic negotiation logic"""
    creator_rate = request.creator_proposal.get('rate', 0)
    max_budget = request.brand_constraints.get('max_budget', 0)
    
    if creator_rate <= max_budget:
        return NegotiationResponse(
            action="accept",
            message=f"Great! We can work with your proposed rate of ${creator_rate}. Let's move forward with the campaign.",
            proposed_terms=request.creator_proposal
        )
    elif creator_rate <= max_budget * 1.2:  # Within 20% of budget
        counter_offer = int(max_budget * 0.9)
        return NegotiationResponse(
            action="counter",
            message=f"Thanks for your proposal! Our budget for this campaign is ${counter_offer}. Would this work for you?",
            proposed_terms={**request.creator_proposal, "rate": counter_offer}
        )
    else:
        return NegotiationResponse(
            action="reject",
            message="Thank you for your interest. Unfortunately, your rate is outside our current budget range. We'll keep you in mind for future campaigns with larger budgets."
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-communication"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
