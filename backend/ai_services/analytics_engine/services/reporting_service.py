 # Report generation

# backend/ai_services/analytics_engine/services/reporting_service.py
from schemas.analytics_schemas import AnalyticsResponse
from utils.data_aggregation import DataAggregator
import sys

class ReportingService:
    def generate_report(self, data: list) -> AnalyticsResponse:
        return AnalyticsResponse(
            success=True,
            data=DataAggregator.calculate_engagement_metrics(data)
        )
