from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CampaignCreate(BaseModel):
    brand_name: str
    campaign_name: str
    description: Optional[str] = None
    target_audience: str
    budget_range: str
    timeline: str
    platforms: List[str]
    content_types: List[str]
    campaign_goals: List[str]
    deliverables: Optional[List[Dict[str, Any]]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignResponse(BaseModel):
    id: str
    brand_name: str
    campaign_name: str
    description: Optional[str]
    target_audience: str
    budget_range: str
    timeline: str
    deliverables: List[Dict[str, Any]]
    status: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

class CampaignUpdate(BaseModel):
    brand_name: Optional[str]
    campaign_name: Optional[str]
    description: Optional[str]
    target_audience: Optional[str]
    budget_range: Optional[str]
    timeline: Optional[str]
    platforms: Optional[List[str]]
    content_types: Optional[List[str]]
    campaign_goals: Optional[List[str]]
    deliverables: Optional[List[Dict[str, Any]]]
    status: Optional[str]
