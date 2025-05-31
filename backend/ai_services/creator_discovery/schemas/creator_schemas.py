from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class CreatorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query for creators")
    limit: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")
    include_embeddings: bool = Field(default=False, description="Include embedding data in response")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class CreatorDemographics(BaseModel):
    age_group: Optional[str] = None
    gender_split: Optional[Dict[str, int]] = None
    top_locations: Optional[List[str]] = None
    primary_language: Optional[str] = None

class CreatorRecommendation(BaseModel):
    creator_id: str
    name: str
    handle: Optional[str] = None
    platform: str
    followers: int = Field(ge=0)
    engagement_rate: float = Field(ge=0.0, le=100.0)
    categories: List[str] = []
    demographics: Optional[CreatorDemographics] = None
    content_style: Optional[str] = None
    location: Optional[str] = None
    collaboration_rate: Optional[str] = None
    response_rate: Optional[int] = Field(default=None, ge=0, le=100)
    match_score: float = Field(ge=0.0, le=100.0, description="AI-calculated match score")
    creator_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    language: Optional[str] = "English"
    verified: Optional[bool] = False
    last_active: Optional[datetime] = None

class CreatorSearchResponse(BaseModel):
    results: List[CreatorRecommendation]
    total_found: int = Field(ge=0)
    query: str
    search_time_ms: Optional[float] = None
    used_cache: bool = False
    filters_applied: Optional[Dict[str, Any]] = None

class CreatorDetailRequest(BaseModel):
    creator_id: str = Field(..., min_length=1)
    include_similar: bool = Field(default=False)
    similar_count: int = Field(default=5, ge=1, le=20)

class CreatorProfile(BaseModel):
    creator_id: str
    name: str
    handle: Optional[str] = None
    platform: str
    bio: Optional[str] = None
    followers: int = Field(ge=0)
    following: Optional[int] = Field(default=None, ge=0)
    total_posts: Optional[int] = Field(default=None, ge=0)
    engagement_rate: float = Field(ge=0.0, le=100.0)
    avg_likes: Optional[int] = Field(default=None, ge=0)
    avg_comments: Optional[int] = Field(default=None, ge=0)
    avg_shares: Optional[int] = Field(default=None, ge=0)
    categories: List[str] = []
    demographics: Optional[CreatorDemographics] = None
    content_style: Optional[str] = None
    location: Optional[str] = None
    collaboration_rate: Optional[str] = None
    response_rate: Optional[int] = Field(default=None, ge=0, le=100)
    creator_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    language: Optional[str] = "English"
    verified: bool = False
    profile_image_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CreatorDetailResponse(BaseModel):
    creator: CreatorProfile
    similar_creators: Optional[List[CreatorRecommendation]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

class SearchFilters(BaseModel):
    platform: Optional[str] = None
    min_followers: Optional[int] = Field(default=None, ge=0)
    max_followers: Optional[int] = Field(default=None, ge=0)
    min_engagement_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    max_engagement_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    categories: Optional[List[str]] = None
    location: Optional[str] = None
    language: Optional[str] = None
    age_group: Optional[str] = None
    verified_only: Optional[bool] = False
    response_rate_min: Optional[int] = Field(default=None, ge=0, le=100)
    
    @validator('max_followers')
    def validate_follower_range(cls, v, values):
        if v is not None and 'min_followers' in values and values['min_followers'] is not None:
            if v < values['min_followers']:
                raise ValueError('max_followers must be greater than min_followers')
        return v
    
    @validator('max_engagement_rate')
    def validate_engagement_range(cls, v, values):
        if v is not None and 'min_engagement_rate' in values and values['min_engagement_rate'] is not None:
            if v < values['min_engagement_rate']:
                raise ValueError('max_engagement_rate must be greater than min_engagement_rate')
        return v

class BatchSearchRequest(BaseModel):
    queries: List[str] = Field(..., min_items=1, max_items=10)
    limit_per_query: int = Field(default=5, ge=1, le=20)
    common_filters: Optional[SearchFilters] = None

class BatchSearchResponse(BaseModel):
    results: Dict[str, CreatorSearchResponse]
    total_queries: int
    processing_time_ms: Optional[float] = None

class CreatorIndexRequest(BaseModel):
    creator_data: CreatorProfile
    generate_embedding: bool = Field(default=True)
    update_if_exists: bool = Field(default=True)

class CreatorIndexResponse(BaseModel):
    creator_id: str
    indexed: bool
    embedding_generated: bool
    message: str
    indexed_at: datetime

class SimilarCreatorsRequest(BaseModel):
    creator_id: str = Field(..., min_length=1)
    count: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    exclude_same_platform: bool = Field(default=False)

class SimilarCreatorsResponse(BaseModel):
    reference_creator: CreatorRecommendation
    similar_creators: List[CreatorRecommendation]
    similarity_method: str = "semantic_embedding"

class SearchAnalytics(BaseModel):
    query: str
    results_count: int
    search_time_ms: float
    used_cache: bool
    timestamp: datetime
    user_id: Optional[str] = None

class CreatorAnalytics(BaseModel):
    creator_id: str
    view_count: int = 0
    search_appearances: int = 0
    click_through_rate: Optional[float] = None
    last_viewed: Optional[datetime] = None

class DiscoveryHealthCheck(BaseModel):
    service_status: str = "healthy"
    database_connected: bool
    redis_connected: bool
    embedding_service_status: str
    vector_store_status: str
    total_creators_indexed: int
    last_index_update: Optional[datetime] = None

# Error schemas
class SearchError(BaseModel):
    error_type: str
    message: str
    query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    field: str
    message: str
    invalid_value: Optional[Any] = None