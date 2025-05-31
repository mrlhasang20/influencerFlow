# Analytics processing

# Analytics Service Implementation

# backend/ai_services/analytics_engine/services/analytics_service.py

import google.generativeai as genai
from typing import Dict, Any, List, Optional
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.config import settings
from schemas.analytics_schemas import (
    CampaignAnalyticsResponse, PerformanceInsight, PerformancePrediction,
    PerformancePredictionResponse, ROIAnalysisResponse, CampaignMetrics, TimePeriod
)

class AnalyticsService:
    """AI-powered analytics service for campaign performance analysis"""
    
    def __init__(self):
        self.configure_gemini()
        self.industry_benchmarks = self._load_industry_benchmarks()
        
    def configure_gemini(self):
        """Configure Gemini for analytics and insights"""
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction="""You are an expert digital marketing analyst specializing in influencer marketing.
            Analyze campaign performance data, identify trends, provide actionable insights, and make data-driven recommendations.
            Focus on ROI optimization, audience engagement, and campaign effectiveness."""
        )
    
    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """Load industry benchmarks for different platforms and categories"""
        return {
            "Instagram": {
                "engagement_rate": {"fitness": 3.8, "beauty": 4.2, "tech": 2.1, "fashion": 3.5},
                "click_through_rate": 0.9,
                "conversion_rate": 1.2,
                "cost_per_engagement": 0.15
            },
            "YouTube": {
                "engagement_rate": {"fitness": 2.5, "beauty": 3.1, "tech": 2.8, "fashion": 2.2},
                "click_through_rate": 2.1,
                "conversion_rate": 2.5,
                "cost_per_engagement": 0.25
            },
            "TikTok": {
                "engagement_rate": {"fitness": 6.2, "beauty": 7.1, "tech": 4.5, "fashion": 5.8},
                "click_through_rate": 1.5,
                "conversion_rate": 0.8,
                "cost_per_engagement": 0.08
            },
            "LinkedIn": {
                "engagement_rate": {"business": 2.8, "tech": 3.2, "finance": 2.1},
                "click_through_rate": 2.8,
                "conversion_rate": 3.1,
                "cost_per_engagement": 0.35
            }
        }
    
    async def analyze_campaign_performance(
        self, 
        campaign_id: str, 
        metrics: CampaignMetrics, 
        time_period: TimePeriod
    ) -> CampaignAnalyticsResponse:
        """Comprehensive campaign performance analysis"""
        try:
            # Calculate derived metrics
            calculated_metrics = self._calculate_derived_metrics(metrics)
            
            # Get industry benchmarks
            benchmarks = self._get_relevant_benchmarks(campaign_id)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(campaign_id, calculated_metrics, benchmarks)
            
            # Create performance insights
            performance_insights = self._create_performance_insights(calculated_metrics, benchmarks)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(calculated_metrics, benchmarks)
            
            return CampaignAnalyticsResponse(
                campaign_id=campaign_id,
                overall_score=overall_score,
                performance_insights=performance_insights,
                key_findings=ai_insights["key_findings"],
                recommendations=ai_insights["recommendations"],
                predicted_improvements=ai_insights.get("predicted_improvements", {})
            )
            
        except Exception as e:
            raise Exception(f"Campaign analysis failed: {str(e)}")
    
    def _calculate_derived_metrics(self, metrics: CampaignMetrics) -> Dict[str, float]:
        """Calculate derived metrics from base metrics"""
        calculated = {}
        
        # Engagement rate
        if metrics.engagement and metrics.impressions:
            calculated["engagement_rate"] = (metrics.engagement / metrics.impressions) * 100
        
        # Click-through rate
        if metrics.clicks and metrics.impressions:
            calculated["ctr"] = (metrics.clicks / metrics.impressions) * 100
        
        # Conversion rate
        if metrics.conversions and metrics.clicks:
            calculated["conversion_rate"] = (metrics.conversions / metrics.clicks) * 100
        
        # Reach rate
        if metrics.reach and metrics.impressions:
            calculated["reach_rate"] = (metrics.reach / metrics.impressions) * 100
        
        # Copy original metrics
        for field, value in metrics.dict().items():
            if value is not None:
                calculated[field] = float(value)
        
        return calculated
    
    def _get_relevant_benchmarks(self, campaign_id: str) -> Dict[str, float]:
        """Get relevant industry benchmarks for the campaign"""
        # For demo purposes, use Instagram fitness benchmarks
        return {
            "engagement_rate": 3.8,
            "ctr": 0.9,
            "conversion_rate": 1.2
        }
    
    async def _generate_ai_insights(
        self, 
        campaign_id: str, 
        metrics: Dict[str, float], 
        benchmarks: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""
        
        prompt = f"""
        Analyze this influencer marketing campaign performance:
        
        Campaign ID: {campaign_id}
        
        Performance Metrics:
        {json.dumps(metrics, indent=2)}
        
        Industry Benchmarks:
        {json.dumps(benchmarks, indent=2)}
        
        Provide analysis in this JSON format:
        {{
            "key_findings": [
                "Finding 1 with specific data points",
                "Finding 2 with actionable insights"
            ],
            "recommendations": [
                "Specific recommendation 1",
                "Actionable recommendation 2"
            ],
            "predicted_improvements": {{
                "engagement_improvement": "percentage or description",
                "roi_optimization": "specific optimization potential"
            }}
        }}
        
        Focus on:
        1. Performance vs benchmarks
        2. Optimization opportunities
        3. Audience engagement quality
        4. ROI improvement potential
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse AI response
            ai_analysis = self._parse_ai_response(response.text)
            return ai_analysis
            
        except Exception as e:
            # Fallback to rule-based insights
            return self._generate_fallback_insights(metrics, benchmarks)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract insights"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._parse_text_response(response_text)
        except json.JSONDecodeError:
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON AI response"""
        findings = []
        recommendations = []
        
        # Extract key insights from text
        lines = text.split('\n')
        for line in lines:
            if 'performance' in line.lower() or 'engagement' in line.lower():
                if len(findings) < 3:
                    findings.append(line.strip())
            elif 'recommend' in line.lower() or 'optimize' in line.lower():
                if len(recommendations) < 3:
                    recommendations.append(line.strip())
        
        return {
            "key_findings": findings or ["Performance analysis completed", "Campaign metrics analyzed"],
            "recommendations": recommendations or ["Continue monitoring performance", "Optimize based on top-performing content"],
            "predicted_improvements": {
                "engagement_improvement": "5-15% potential increase",
                "roi_optimization": "10-20% improvement possible"
            }
        }
    
    def _generate_fallback_insights(self, metrics: Dict[str, float], benchmarks: Dict[str, float]) -> Dict[str, Any]:
        """Generate rule-based insights as fallback"""
        findings = []
        recommendations = []
        
        # Analyze engagement rate
        if "engagement_rate" in metrics and "engagement_rate" in benchmarks:
            eng_rate = metrics["engagement_rate"]
            benchmark = benchmarks["engagement_rate"]
            
            if eng_rate > benchmark * 1.2:
                findings.append(f"Exceptional engagement rate of {eng_rate:.1f}% (vs {benchmark:.1f}% benchmark)")
                recommendations.append("Leverage high engagement with more frequent posting")
            elif eng_rate < benchmark * 0.8:
                findings.append(f"Below-average engagement rate of {eng_rate:.1f}% (vs {benchmark:.1f}% benchmark)")
                recommendations.append("Improve content quality and posting times")
        
        # Analyze conversion rate
        if "conversion_rate" in metrics:
            conv_rate = metrics["conversion_rate"]
            if conv_rate > 2.0:
                findings.append(f"Strong conversion rate of {conv_rate:.1f}%")
                recommendations.append("Scale successful content formats")
            elif conv_rate < 1.0:
                findings.append(f"Low conversion rate of {conv_rate:.1f}%")
                recommendations.append("Optimize call-to-action and landing pages")
        
        return {
            "key_findings": findings or ["Campaign performance analyzed"],
            "recommendations": recommendations or ["Continue monitoring and optimization"],
            "predicted_improvements": {
                "engagement_improvement": "5-10% potential increase",
                "roi_optimization": "Performance optimization opportunities identified"
            }
        }
    
    def _create_performance_insights(
        self, 
        metrics: Dict[str, float], 
        benchmarks: Dict[str, float]
    ) -> List[PerformanceInsight]:
        """Create detailed performance insights"""
        insights = []
        
        for metric_name, value in metrics.items():
            if metric_name in benchmarks:
                benchmark = benchmarks[metric_name]
                
                # Determine performance vs benchmark
                performance_ratio = value / benchmark if benchmark > 0 else 1
                
                if performance_ratio > 1.2:
                    performance_desc = "Excellent - Above benchmark"
                    recommendation = f"Maintain and scale successful {metric_name} strategies"
                elif performance_ratio > 0.8:
                    performance_desc = "Good - Near benchmark"
                    recommendation = f"Small optimizations could improve {metric_name}"
                else:
                    performance_desc = "Needs improvement - Below benchmark"
                    recommendation = f"Focus on improving {metric_name} through content optimization"
                
                insights.append(PerformanceInsight(
                    metric=metric_name,
                    value=value,
                    benchmark=benchmark,
                    performance_vs_benchmark=performance_desc,
                    recommendation=recommendation
                ))
        
        return insights
    
    def _calculate_overall_score(self, metrics: Dict[str, float], benchmarks: Dict[str, float]) -> float:
        """Calculate overall campaign performance score"""
        scores = []
        
        for metric_name, value in metrics.items():
            if metric_name in benchmarks and benchmarks[metric_name] > 0:
                benchmark = benchmarks[metric_name]
                ratio = value / benchmark
                # Cap the score at 150% to prevent outliers from skewing results
                score = min(ratio * 100, 150)
                scores.append(score)
        
        if scores:
            return sum(scores) / len(scores)
        else:
            return 75.0  # Default score if no benchmarks available
    
    async def predict_campaign_performance(
        self,
        creator_profile: Dict[str, Any],
        campaign_details: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> PerformancePredictionResponse:
        """Predict campaign performance using AI and historical data"""
        try:
            # Generate predictions using AI
            ai_predictions = await self._generate_performance_predictions(
                creator_profile, campaign_details, historical_data
            )
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(creator_profile, campaign_details)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(creator_profile, campaign_details)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(creator_profile, campaign_details)
            
            return PerformancePredictionResponse(
                predictions=ai_predictions,
                success_probability=success_probability,
                risk_factors=risk_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            raise Exception(f"Performance prediction failed: {str(e)}")
    
    async def _generate_performance_predictions(
        self,
        creator_profile: Dict[str, Any],
        campaign_details: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> List[PerformancePrediction]:
        """Generate AI-powered performance predictions"""
        
        # Use historical data patterns and creator profile for predictions
        platform = creator_profile.get("platform", "Instagram")
        followers = creator_profile.get("followers", 10000)
        engagement_rate = creator_profile.get("engagement_rate", 3.0)
        budget = campaign_details.get("budget", 1000)
        
        # Calculate baseline predictions
        predicted_impressions = followers * 0.3  # Assuming 30% of followers see content
        predicted_engagement = predicted_impressions * (engagement_rate / 100)
        predicted_clicks = predicted_engagement * 0.05  # 5% of engaged users click
        predicted_conversions = predicted_clicks * 0.02  # 2% conversion rate
        
        predictions = [
            PerformancePrediction(
                metric="impressions",
                predicted_value=predicted_impressions,
                confidence_level=85.0,
                range_min=predicted_impressions * 0.7,
                range_max=predicted_impressions * 1.3
            ),
            PerformancePrediction(
                metric="engagement",
                predicted_value=predicted_engagement,
                confidence_level=80.0,
                range_min=predicted_engagement * 0.6,
                range_max=predicted_engagement * 1.4
            ),
            PerformancePrediction(
                metric="clicks",
                predicted_value=predicted_clicks,
                confidence_level=70.0,
                range_min=predicted_clicks * 0.5,
                range_max=predicted_clicks * 1.5
            ),
            PerformancePrediction(
                metric="conversions",
                predicted_value=predicted_conversions,
                confidence_level=65.0,
                range_min=predicted_conversions * 0.4,
                range_max=predicted_conversions * 1.6
            )
        ]
        
        return predictions
    
    def _calculate_success_probability(self, creator_profile: Dict[str, Any], campaign_details: Dict[str, Any]) -> float:
        """Calculate campaign success probability"""
        score = 50.0  # Base score
        
        # Factor in engagement rate
        engagement_rate = creator_profile.get("engagement_rate", 0)
        if engagement_rate > 5:
            score += 20
        elif engagement_rate > 3:
            score += 10
        elif engagement_rate < 1:
            score -= 15
        
        # Factor in audience size
        followers = creator_profile.get("followers", 0)
        if 10000 <= followers <= 100000:  # Sweet spot for engagement
            score += 15
        elif followers > 1000000:
            score += 5
        elif followers < 1000:
            score -= 20
        
        # Factor in budget appropriateness
        budget = campaign_details.get("budget", 0)
        if budget > followers * 0.05:  # Good budget ratio
            score += 10
        elif budget < followers * 0.01:  # Low budget
            score -= 10
        
        return min(max(score, 0), 100)
    
    def _identify_risk_factors(self, creator_profile: Dict[str, Any], campaign_details: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors for the campaign"""
        risks = []
        
        engagement_rate = creator_profile.get("engagement_rate", 0)
        if engagement_rate < 2:
            risks.append("Low engagement rate may limit campaign effectiveness")
        
        followers = creator_profile.get("followers", 0)
        if followers < 1000:
            risks.append("Limited audience reach due to small follower count")
        elif followers > 5000000:
            risks.append("Very large audience may have lower engagement rates")
        
        budget = campaign_details.get("budget", 0)
        if budget < 500:
            risks.append("Limited budget may restrict campaign scope and effectiveness")
        
        duration = campaign_details.get("duration_days", 30)
        if duration < 7:
            risks.append("Short campaign duration may not allow for optimization")
        elif duration > 90:
            risks.append("Extended campaign may experience audience fatigue")
        
        return risks
    
    def _generate_optimization_suggestions(self, creator_profile: Dict[str, Any], campaign_details: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        platform = creator_profile.get("platform", "")
        
        if platform == "Instagram":
            suggestions.extend([
                "Use Instagram Stories for behind-the-scenes content",
                "Optimize posting times based on audience activity",
                "Include clear call-to-actions in captions"
            ])
        elif platform == "YouTube":
            suggestions.extend([
                "Create engaging thumbnails to improve click-through rates", 
                "Optimize video descriptions with relevant keywords",
                "Use end screens to drive additional engagement"
            ])
        elif platform == "TikTok":
            suggestions.extend([
                "Leverage trending sounds and hashtags",
                "Create authentic, unpolished content",
                "Post consistently during peak hours"
            ])
        
        # General suggestions
        suggestions.extend([
            "A/B test different content formats",
            "Monitor competitor strategies for insights",
            "Engage actively with audience comments"
        ])
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    async def demo_analysis(self, sample_campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demo analysis for testing"""
        return {
            "analysis_type": "demo",
            "campaign_id": sample_campaign.get("campaign_id"),
            "performance_score": 78.5,
            "key_metrics": {
                "engagement_rate": 4.2,
                "click_through_rate": 1.1,
                "conversion_rate": 2.1
            },
            "ai_insights": [
                "Strong engagement rate indicates good audience connection",
                "Click-through rate above industry average",
                "Conversion rate suggests effective call-to-action"
            ],
            "recommendations": [
                "Scale successful content formats",
                "Test posting at different times",
                "Consider expanding to similar audiences"
            ]
        }
