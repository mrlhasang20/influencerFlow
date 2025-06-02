 # Campaign analytics

# backend/ai_services/analytics_engine/models/performance_analyzer.py
class PerformanceAnalyzer:
    def analyze_engagement(self, data: list) -> dict:
        return {"engagement_rate": sum(item.get("likes",0) for item in data)/len(data) if data else 0}
