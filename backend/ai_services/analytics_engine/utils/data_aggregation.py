# backend/ai_services/analytics_engine/utils/data_aggregation.py
from typing import List, Dict
import numpy as np

class DataAggregator:
    @staticmethod
    def calculate_engagement_metrics(data: List[Dict]) -> Dict:
        total_engagement = sum(
            item.get("likes", 0) + 
            item.get("comments", 0) + 
            item.get("shares", 0) 
            for item in data
        )
        return {"total_engagement": total_engagement}
