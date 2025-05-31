 # Social media metrics

# backend/ai_services/analytics_engine/models/social_metrics.py
class SocialMetrics:
    @staticmethod
    def calculate_virality(shares: int, impressions: int) -> float:
        return (shares / impressions) * 100 if impressions else 0.0
