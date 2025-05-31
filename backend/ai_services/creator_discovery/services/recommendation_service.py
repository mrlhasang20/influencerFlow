from typing import List, Dict, Optional
import asyncio
import time
from models.search_engine import SemanticSearchEngine
from models.vector_db import CreatorVectorDB
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from schemas.creator_schemas import (
    CreatorSearchRequest, CreatorSearchResponse, CreatorRecommendation,
    SimilarCreatorsRequest, SimilarCreatorsResponse, SearchFilters
)
from shared.config import DEMO_CREATORS
from shared.utils import Timer, calculate_creator_score, categorize_follower_count
from shared.redis_client import redis_client

class CreatorRecommendationService:
    def __init__(self):
        self.search_engine = SemanticSearchEngine()
        self.vector_db = CreatorVectorDB()
        self.creators_data = DEMO_CREATORS
        self._initialized = False
    
    async def initialize(self):
        """Initialize the service with creator embeddings"""
        if self._initialized:
            return
        
        try:
            print("🚀 Initializing Creator Recommendation Service...")
            
            # Index all demo creators for faster searching
            await self.vector_db.batch_index_creators(self.creators_data)
            
            self._initialized = True
            print("✅ Creator Recommendation Service initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize service: {e}")
    
    async def search_creators(self, request: CreatorSearchRequest) -> CreatorSearchResponse:
        """Search for creators using AI-powered semantic search"""
        start_time = time.time()
        
        try:
            # Ensure service is initialized
            await self.initialize()
            
            with Timer(f"Creator search for query: '{request.query}'"):
                # Convert filters to dict if provided
                filters = None
                if request.filters:
                    filters = request.filters
                
                # Perform semantic search
                search_results = await self.search_engine.search_creators(
                    query=request.query,
                    creators=self.creators_data,
                    top_k=request.limit,
                    filters=filters,
                    similarity_threshold=0.2  # Lower threshold for demo
                )
                
                # Convert to response format
                recommendations = []
                for result in search_results:
                    recommendation = CreatorRecommendation(
                        creator_id=result["creator_id"],
                        name=result["name"],
                        handle=result.get("handle"),
                        platform=result["platform"],
                        followers=result["followers"],
                        engagement_rate=result["engagement_rate"],
                        categories=result["categories"],
                        demographics=result.get("demographics"),
                        content_style=result.get("content_style"),
                        location=result.get("location"),
                        collaboration_rate=result.get("collaboration_rate"),
                        response_rate=result.get("response_rate"),
                        match_score=result["match_score"],
                        creator_score=result.get("creator_score"),
                        language=result.get("language", "English")
                    )
                    recommendations.append(recommendation)
                
                search_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return CreatorSearchResponse(
                    results=recommendations,
                    total_found=len(recommendations),
                    query=request.query,
                    search_time_ms=search_time,
                    used_cache=False,  # Would be determined by cache hit
                    filters_applied=filters
                )
                
        except Exception as e:
            print(f"Search error: {e}")
            # Return empty results on error
            return CreatorSearchResponse(
                results=[],
                total_found=0,
                query=request.query,
                search_time_ms=(time.time() - start_time) * 1000
            )
    
    async def get_similar_creators(self, request: SimilarCreatorsRequest) -> SimilarCreatorsResponse:
        """Get creators similar to a reference creator"""
        try:
            # Ensure service is initialized
            await self.initialize()
            
            # Get reference creator data
            reference_creator_data = self.creators_data.get(request.creator_id)
            if not reference_creator_data:
                raise ValueError(f"Creator {request.creator_id} not found")
            
            # Get similar creators using search engine
            similar_results = await self.search_engine.get_recommendations(
                creator_id=request.creator_id,
                creators=self.creators_data,
                count=request.count
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in similar_results
                if result["match_score"] / 100 >= request.similarity_threshold
            ]
            
            # Apply platform filter if requested
            if request.exclude_same_platform:
                reference_platform = reference_creator_data.get("platform", "")
                filtered_results = [
                    result for result in filtered_results
                    if result["platform"] != reference_platform
                ]
            
            # Convert to recommendations
            similar_recommendations = []
            for result in filtered_results:
                recommendation = CreatorRecommendation(
                    creator_id=result["creator_id"],
                    name=result["name"],
                    handle=result.get("handle"),
                    platform=result["platform"],
                    followers=result["followers"],
                    engagement_rate=result["engagement_rate"],
                    categories=result["categories"],
                    demographics=result.get("demographics"),
                    content_style=result.get("content_style"),
                    location=result.get("location"),
                    collaboration_rate=result.get("collaboration_rate"),
                    response_rate=result.get("response_rate"),
                    match_score=result["match_score"],
                    creator_score=result.get("creator_score"),
                    language=result.get("language", "English")
                )
                similar_recommendations.append(recommendation)
            
            # Create reference creator recommendation
            reference_recommendation = CreatorRecommendation(
                creator_id=request.creator_id,
                name=reference_creator_data["name"],
                handle=reference_creator_data.get("handle"),
                platform=reference_creator_data["platform"],
                followers=reference_creator_data["followers"],
                engagement_rate=reference_creator_data["engagement_rate"],
                categories=reference_creator_data["categories"],
                demographics=reference_creator_data.get("demographics"),
                content_style=reference_creator_data.get("content_style"),
                location=reference_creator_data.get("location"),
                collaboration_rate=reference_creator_data.get("collaboration_rate"),
                response_rate=reference_creator_data.get("response_rate"),
                match_score=100.0,  # Perfect match with itself
                creator_score=calculate_creator_score(
                    reference_creator_data.get("engagement_rate", 0),
                    reference_creator_data.get("followers", 0),
                    reference_creator_data.get("response_rate", 50)
                ),
                language=reference_creator_data.get("language", "English")
            )
            
            return SimilarCreatorsResponse(
                reference_creator=reference_recommendation,
                similar_creators=similar_recommendations
            )
            
        except Exception as e:
            print(f"Similar creators error: {e}")
            raise
    
    async def get_recommendations_by_category(
        self,
        category: str,
        count: int = 10,
        min_followers: int = 1000
    ) -> List[CreatorRecommendation]:
        """Get top creators in a specific category"""
        try:
            # Filter creators by category
            category_creators = {}
            for creator_id, creator_data in self.creators_data.items():
                if (category.lower() in [cat.lower() for cat in creator_data.get("categories", [])] and
                    creator_data.get("followers", 0) >= min_followers):
                    category_creators[creator_id] = creator_data
            
            if not category_creators:
                return []
            
            # Sort by engagement rate and follower count
            sorted_creators = sorted(
                category_creators.items(),
                key=lambda x: (x[1].get("engagement_rate", 0), x[1].get("followers", 0)),
                reverse=True
            )
            
            # Take top creators and convert to recommendations
            recommendations = []
            for creator_id, creator_data in sorted_creators[:count]:
                recommendation = CreatorRecommendation(
                    creator_id=creator_id,
                    name=creator_data["name"],
                    handle=creator_data.get("handle"),
                    platform=creator_data["platform"],
                    followers=creator_data["followers"],
                    engagement_rate=creator_data["engagement_rate"],
                    categories=creator_data["categories"],
                    demographics=creator_data.get("demographics"),
                    content_style=creator_data.get("content_style"),
                    location=creator_data.get("location"),
                    collaboration_rate=creator_data.get("collaboration_rate"),
                    response_rate=creator_data.get("response_rate"),
                    match_score=95.0,  # High score for category match
                    creator_score=calculate_creator_score(
                        creator_data.get("engagement_rate", 0),
                        creator_data.get("followers", 0),
                        creator_data.get("response_rate", 50)
                    ),
                    language=creator_data.get("language", "English")
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"Category recommendations error: {e}")
            return []
    
    async def get_trending_creators(self, count: int = 10) -> List[CreatorRecommendation]:
        """Get trending creators based on engagement and growth metrics"""
        try:
            # Simple trending algorithm based on engagement rate and follower count
            creator_scores = []
            
            for creator_id, creator_data in self.creators_data.items():
                # Calculate trending score
                engagement = creator_data.get("engagement_rate", 0)
                followers = creator_data.get("followers", 0)
                response_rate = creator_data.get("response_rate", 50)
                
                # Weighted scoring for trending
                trending_score = (
                    engagement * 0.4 +  # 40% weight on engagement
                    min(followers / 10000, 50) * 0.3 +  # 30% weight on followers (capped)
                    response_rate * 0.3  # 30% weight on response rate
                )
                
                creator_scores.append((creator_id, creator_data, trending_score))
            
            # Sort by trending score
            creator_scores.sort(key=lambda x: x[2], reverse=True)
            
            # Convert top creators to recommendations
            recommendations = []
            for creator_id, creator_data, score in creator_scores[:count]:
                recommendation = CreatorRecommendation(
                    creator_id=creator_id,
                    name=creator_data["name"],
                    handle=creator_data.get("handle"),
                    platform=creator_data["platform"],
                    followers=creator_data["followers"],
                    engagement_rate=creator_data["engagement_rate"],
                    categories=creator_data["categories"],
                    demographics=creator_data.get("demographics"),
                    content_style=creator_data.get("content_style"),
                    location=creator_data.get("location"),
                    collaboration_rate=creator_data.get("collaboration_rate"),
                    response_rate=creator_data.get("response_rate"),
                    match_score=min(score * 2, 100),  # Convert to 0-100 scale
                    creator_score=calculate_creator_score(
                        creator_data.get("engagement_rate", 0),
                        creator_data.get("followers", 0),
                        creator_data.get("response_rate", 50)
                    ),
                    language=creator_data.get("language", "English")
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"Trending creators error: {e}")
            return []
    
    def get_creator_statistics(self) -> Dict:
        """Get statistics about the creator database"""
        try:
            stats = {
                "total_creators": len(self.creators_data),
                "platforms": {},
                "categories": {},
                "total_followers": 0,
                "avg_engagement_rate": 0,
                "avg_response_rate": 0
            }
            
            engagement_rates = []
            response_rates = []
            
            for creator_data in self.creators_data.values():
                # Platform distribution
                platform = creator_data.get("platform", "Unknown")
                stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1
                
                # Category distribution
                for category in creator_data.get("categories", []):
                    stats["categories"][category] = stats["categories"].get(category, 0) + 1
                
                # Metrics
                stats["total_followers"] += creator_data.get("followers", 0)
                
                engagement_rate = creator_data.get("engagement_rate", 0)
                if engagement_rate > 0:
                    engagement_rates.append(engagement_rate)
                
                response_rate = creator_data.get("response_rate", 0)
                if response_rate > 0:
                    response_rates.append(response_rate)
            
            # Calculate averages
            if engagement_rates:
                stats["avg_engagement_rate"] = sum(engagement_rates) / len(engagement_rates)
            
            if response_rates:
                stats["avg_response_rate"] = sum(response_rates) / len(response_rates)
            
            return stats
            
        except Exception as e:
            print(f"Statistics error: {e}")
            return {}