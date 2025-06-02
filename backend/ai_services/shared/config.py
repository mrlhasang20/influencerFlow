# Shared Configuration File - config.py

import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Google Gemini API Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_api_key: str = os.getenv("GOOGLE_API_KEY", "")  # Alias for compatibility
    database_url: str = os.getenv("DATABASE_URL", "")
    demo_mode: bool = True
    vector_dimension: int = 768
    vector_collection_name: str = "creator_embeddings"
    default_similarity_threshold: float = 0.5
    max_search_results: int = 100
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    rate_limit_per_minute: int = 60
    allowed_origins: List[str] = ["http://localhost:3000", "https://yourdomain.com"]
    default_model: str = "gemini-pro"
    embedding_model: str = "text-embedding-004"
    max_tokens: int = 1000
    temperature: float = 0.7

    # Original settings
    gemini_model: str = "gemini-1.5-flash"
    gemini_embedding_model: str = "text-embedding-004"
    postgres_url: str = os.getenv("DATABASE_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "")
    creator_discovery_port: int = 8001
    ai_communication_port: int = 8002
    contract_automation_port: int = 8003
    analytics_engine_port: int = 8004
    api_gateway_port: int = 8000
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    cache_ttl: int = 3600
    embedding_cache_ttl: int = 86400
    deepl_api_key: Optional[str] = os.getenv("DEEPL_API_KEY")
    elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Service URLs for internal communication
SERVICE_URLS = {
    "creator_discovery": f"http://localhost:{settings.creator_discovery_port}",
    "ai_communication": f"http://localhost:{settings.ai_communication_port}",
    "contract_automation": f"http://localhost:{settings.contract_automation_port}",
    "analytics_engine": f"http://localhost:{settings.analytics_engine_port}"
}

# Gemini Model Configuration
GEMINI_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
    "safety_settings": [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH", 
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
}

# Vector Database Configuration
VECTOR_CONFIG = {
    "dimension": 768,  # text-embedding-004 dimension
    "index_type": "HNSW",
    "metric": "cosine",
    "ef_construction": 200,
    "m": 16
}

# Mock Data Configuration for Demo
DEMO_CREATORS = {
    "creator_1": {
        "id": "creator_1",
        "name": "Sarah Johnson",
        "handle": "@sarahfitlife",
        "platform": "Instagram",
        "followers": 150000,
        "engagement_rate": 4.2,
        "categories": ["fitness", "health", "wellness", "lifestyle"],
        "demographics": {
            "age_group": "18-34",
            "gender_split": {"female": 65, "male": 35},
            "top_locations": ["United States", "Canada", "Australia"]
        },
        "content_style": "Motivational fitness content with focus on body positivity and mental health",
        "language": "English",
        "location": "Los Angeles, CA",
        "avg_likes": 6300,
        "avg_comments": 180,
        "collaboration_rate": "$500-800",
        "response_rate": 85
    },
    "creator_2": {
        "id": "creator_2",
        "name": "Alex Chen", 
        "handle": "@techreviewalex",
        "platform": "YouTube",
        "followers": 300000,
        "engagement_rate": 6.8,
        "categories": ["technology", "reviews", "gadgets", "innovation"],
        "demographics": {
            "age_group": "25-45",
            "gender_split": {"male": 70, "female": 30},
            "top_locations": ["United States", "Canada", "United Kingdom"]
        },
        "content_style": "Detailed tech reviews and unboxing videos with technical deep-dives",
        "language": "English",
        "location": "Toronto, Canada", 
        "avg_views": 45000,
        "avg_comments": 320,
        "collaboration_rate": "$1000-1500",
        "response_rate": 92
    },
    "creator_3": {
        "id": "creator_3",
        "name": "Maria Rodriguez",
        "handle": "@mariafashion",
        "platform": "TikTok",
        "followers": 450000,
        "engagement_rate": 8.5,
        "categories": ["fashion", "beauty", "lifestyle", "trends"],
        "demographics": {
            "age_group": "16-28",
            "gender_split": {"female": 85, "male": 15},
            "top_locations": ["United States", "Mexico", "Spain"]
        },
        "content_style": "Trendy fashion content with affordable style tips and beauty tutorials",
        "language": "English/Spanish",
        "location": "Miami, FL",
        "avg_views": 85000,
        "avg_shares": 1200,
        "collaboration_rate": "$800-1200",
        "response_rate": 78
    },
    "creator_4": {
        "id": "creator_4",
        "name": "James Wilson",
        "handle": "@gameplayjames",
        "platform": "Twitch",
        "followers": 85000,
        "engagement_rate": 12.3,
        "categories": ["gaming", "esports", "streaming", "entertainment"],
        "demographics": {
            "age_group": "18-35",
            "gender_split": {"male": 80, "female": 20},
            "top_locations": ["United States", "Germany", "Brazil"]
        },
        "content_style": "Live gaming streams with focus on competitive esports and community building",
        "language": "English",
        "location": "Austin, TX",
        "avg_viewers": 2500,
        "avg_chat_messages": 450,
        "collaboration_rate": "$300-600",
        "response_rate": 95
    },
    "creator_5": {
        "id": "creator_5",
        "name": "David Kim",
        "handle": "@davidcooks",
        "platform": "Instagram",
        "followers": 220000,
        "engagement_rate": 5.8,
        "categories": ["food", "cooking", "recipes", "lifestyle"],
        "demographics": {
            "age_group": "25-50",
            "gender_split": {"female": 60, "male": 40},
            "top_locations": ["United States", "South Korea", "Japan"]
        },
        "content_style": "Asian fusion cooking tutorials with cultural storytelling",
        "language": "English/Korean",
        "location": "San Francisco, CA",
        "avg_likes": 12700,
        "avg_comments": 290,
        "collaboration_rate": "$600-900",
        "response_rate": 88
    }
}

