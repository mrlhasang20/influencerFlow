# backend/ai_services/analytics_engine/main.py

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any, Optional
import uvicorn
import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to Python path BEFORE importing from shared
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now we can import from shared
from shared.database import get_db
from shared.config import settings

# Then import local modules
from services.analytics_service import AnalyticsService
from services.reporting_service import ReportingService
from schemas.analytics_schemas import (
    CampaignAnalyticsRequest, CampaignAnalyticsResponse,
    PerformancePredictionRequest, PerformancePredictionResponse,
    ROIAnalysisRequest, ROIAnalysisResponse,
    ReportGenerationRequest, ReportResponse
)

app = FastAPI(
    title="Analytics Engine Service",
    version="1.0.0", 
    description="AI-powered campaign analytics and performance prediction"
)

# Initialize services
analytics_service = AnalyticsService()
reporting_service = ReportingService()

@app.post("/analyze-campaign", response_model=CampaignAnalyticsResponse)
async def analyze_campaign(request: CampaignAnalyticsRequest, db: Session = Depends(get_db)):
    """Analyze campaign performance and provide insights"""
    try:
        analysis = await analytics_service.analyze_campaign_performance(
            request.campaign_id,
            request.metrics,
            request.time_period,
            db
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign analysis failed: {str(e)}")

@app.post("/predict-performance", response_model=PerformancePredictionResponse)
async def predict_performance(request: PerformancePredictionRequest):
    """Predict campaign performance using AI models"""
    try:
        campaign_id = request.campaign_details.get("campaign_id")
        predictions = []
        for metric in ["impressions", "engagement"]:  # or your actual logic
            predictions.append({
                "metric": metric,
                "predicted_value": 50000,  # replace with your calculation
                "confidence_score": 0.85,  # replace with your calculation if needed
                "factors_considered": ["historical engagement", "audience match"]  # replace as needed
            })

        return PerformancePredictionResponse(
            campaign_id=campaign_id,
            predictions=predictions,
            success_probability=0.9,
            risk_factors=["low engagement"],
            optimization_suggestions=["Increase posting frequency"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance prediction failed: {str(e)}")

@app.post("/analyze-roi", response_model=ROIAnalysisResponse)
async def analyze_roi(request: ROIAnalysisRequest):
    """Perform comprehensive ROI analysis"""
    try:
        roi_analysis = await analytics_service.analyze_campaign_roi(
            request.campaign_data,
            request.cost_breakdown,
            request.revenue_attribution
        )
        return roi_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI analysis failed: {str(e)}")

@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportGenerationRequest):
    """Generate comprehensive campaign report"""
    try:
        report = await reporting_service.generate_comprehensive_report(
            request.campaign_ids,
            request.report_type,
            request.include_predictions
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/campaign/{campaign_id}/insights")
async def get_campaign_insights(campaign_id: str):
    """Get AI-generated insights for a specific campaign"""
    try:
        insights = await analytics_service.generate_campaign_insights(campaign_id)
        return {"campaign_id": campaign_id, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.get("/trending-metrics")
async def get_trending_metrics():
    """Get trending performance metrics across all campaigns"""
    try:
        trending = await analytics_service.get_trending_metrics()
        return {"trending_metrics": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending metrics failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-engine"}

@app.get("/debug/sample-analysis")
async def debug_sample_analysis():
    """Debug endpoint with sample analytics"""
    sample_campaign = {
        "campaign_id": "demo_campaign_001",
        "creator_profile": {
            "name": "FitnessInfluencer",
            "platform": "Instagram",
            "followers": 150000,
            "engagement_rate": 4.2,
            "categories": ["fitness", "wellness"]
        },
        "metrics": {
            "impressions": 500000,
            "engagement": 21000,
            "clicks": 3500,
            "conversions": 150
        }
    }
    
    try:
        sample_analysis = await analytics_service.demo_analysis(sample_campaign)
        return {"demo_analysis": sample_analysis}
    except Exception as e:
        return {"error": str(e), "status": "demo_failed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.analytics_engine_port)
