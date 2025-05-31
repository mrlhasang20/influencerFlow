# backend/ai_services/analytics_engine/schemas/analytics_schemas.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TimePeriod(BaseModel):
    start_date: datetime
    end_date: datetime

class CampaignMetrics(BaseModel):
    impressions: Optional[int] = None
    engagement: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    reach: Optional[int] = None
    spend: Optional[float] = None
    revenue: Optional[float] = None

class PerformanceInsight(BaseModel):
    metric_name: str
    current_value: float
    benchmark_value: float
    difference_percentage: float
    insight: str
    recommendation: str

class PerformancePrediction(BaseModel):
    metric: str
    predicted_value: float
    confidence_score: float
    factors_considered: List[str]

class PerformancePredictionResponse(BaseModel):
    campaign_id: str
    predictions: List[PerformancePrediction]
    success_probability: float
    risk_factors: List[str]
    optimization_suggestions: List[str]

class ROIAnalysisResponse(BaseModel):
    campaign_id: str
    total_investment: float
    total_revenue: float
    roi_percentage: float
    break_even_point: datetime
    roi_by_platform: Dict[str, float]
    recommendations: List[str]

class CampaignAnalyticsResponse(BaseModel):
    campaign_id: str
    overall_score: float
    performance_insights: List[PerformanceInsight]
    key_findings: List[str]
    recommendations: List[str]
    predicted_improvements: Dict[str, Any]

class AnalyticsRequest(BaseModel):
    campaign_id: str
    metrics: List[str] = ["engagement"]

class AnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

class CampaignAnalyticsRequest(BaseModel):
    campaign_id: str
    metrics: CampaignMetrics
    time_period: TimePeriod

class PerformancePredictionRequest(BaseModel):
    creator_profile: Dict[str, Any]
    campaign_details: Dict[str, Any]
    historical_data: Optional[List[Dict[str, Any]]] = None

class ROIAnalysisRequest(BaseModel):
    campaign_data: Dict[str, Any]
    cost_breakdown: Dict[str, Any]
    revenue_attribution: Dict[str, Any]

class ReportGenerationRequest(BaseModel):
    campaign_ids: List[str]
    report_type: str
    include_predictions: bool = False

class ReportResponse(BaseModel):
    report_id: str
    status: str
    download_url: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
