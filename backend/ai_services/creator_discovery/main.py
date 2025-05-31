from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import time
from contextlib import asynccontextmanager

from services.recommendation_service import CreatorRecommendationService
from services.search_service import CreatorSearchService
from schemas.creator_schemas import (
    CreatorSearchRequest, CreatorSearchResponse, CreatorRecommendation,
    SimilarCreatorsRequest, SimilarCreatorsResponse, BatchSearchRequest, 
    BatchSearchResponse, SearchFilters, DiscoveryHealthCheck
)
from shared.config import settings, DEMO_CREATORS
from shared.utils import Timer, generate_id
from shared.redis_client import redis_client

# Global service instances
recommendation_service = CreatorRecommendationService()
search_service = CreatorSearchService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Creator Discovery Service...")
    try:
        # Initialize services
        await recommendation_service.initialize()
        print("✅ Creator Discovery Service started successfully")
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Creator Discovery Service...")

# FastAPI app with lifespan
app = FastAPI(
    title="Creator Discovery Service",
    description="AI-powered creator discovery and recommendation service using Gemini embeddings",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=DiscoveryHealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_connected = redis_client.exists("test_key") is not None
        
        return DiscoveryHealthCheck(
            service_status="healthy",
            database_connected=True,  # Would check actual DB connection
            redis_connected=redis_connected,
            embedding_service_status="healthy",
            vector_store_status="healthy",
            total_creators_indexed=len(DEMO_CREATORS)
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/search", response_model=CreatorSearchResponse)
async def search_creators(request: CreatorSearchRequest):
    """Search for creators using AI-powered semantic search"""
    try:
        with Timer(f"Creator search API call for query: '{request.query}'"):
            result = await recommendation_service.search_creators(request)
            return result
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/advanced", response_model=CreatorSearchResponse)
async def advanced_search(
    query: str,
    filters: Optional[SearchFilters] = None,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Advanced search with comprehensive filtering"""
    try:
        result = await search_service.advanced_search(
            query=query,
            filters=filters,
            limit=limit
        )
        return result
    except Exception as e:
        print(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")

@app.post("/search/batch", response_model=BatchSearchResponse)
async def batch_search(request: BatchSearchRequest):
    """Perform batch search for multiple queries"""
    try:
        result = await search_service.batch_search(request)
        return result
    except Exception as e:
        print(f"Batch search error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch search failed: {str(e)}")

@app.post("/similar", response_model=SimilarCreatorsResponse)
async def get_similar_creators(request: SimilarCreatorsRequest):
    """Get creators similar to a reference creator"""
    try:
        result = await recommendation_service.get_similar_creators(request)
        return result
    except Exception as e:
        print(f"Similar creators error: {e}")
        raise HTTPException(status_code=500, detail=f"Similar creators search failed: {str(e)}")

@app.get("/recommendations/category/{category}", response_model=List[CreatorRecommendation])
async def get_category_recommendations(
    category: str,
    count: int = Query(default=10, ge=1, le=50),
    min_followers: int = Query(default=1000, ge=0)
):
    """Get top creators in a specific category"""
    try:
        result = await recommendation_service.get_recommendations_by_category(
            category=category,
            count=count,
            min_followers=min_followers
        )
        return result
    except Exception as e:
        print(f"Category recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Category recommendations failed: {str(e)}")

@app.get("/recommendations/trending", response_model=List[CreatorRecommendation])
async def get_trending_creators(count: int = Query(default=10, ge=1, le=50)):
    """Get trending creators based on engagement and growth metrics"""
    try:
        result = await recommendation_service.get_trending_creators(count=count)
        return result
    except Exception as e:
        print(f"Trending creators error: {e}")
        raise HTTPException(status_code=500, detail=f"Trending creators failed: {str(e)}")

@app.get("/search/demographics", response_model=List[CreatorRecommendation])
async def search_by_demographics(
    age_group: str,
    gender: Optional[str] = None,
    locations: Optional[str] = None,  # Comma-separated
    limit: int = Query(default=10, ge=1, le=50)
):
    """Search creators by audience demographics"""
    try:
        target_locations = None
        if locations:
            target_locations = [loc.strip() for loc in locations.split(",")]
        
        result = await search_service.search_by_audience_demographics(
            target_age_group=age_group,
            target_gender=gender,
            target_locations=target_locations,
            limit=limit
        )
        return result
    except Exception as e:
        print(f"Demographic search error: {e}")
        raise HTTPException(status_code=500, detail=f"Demographic search failed: {str(e)}")

@app.get("/search/performance", response_model=List[CreatorRecommendation])
async def search_by_performance(
    min_engagement_rate: float = Query(ge=0.0, le=100.0),
    min_followers: int = Query(ge=0),
    min_response_rate: Optional[int] = Query(default=None, ge=0, le=100),
    platforms: Optional[str] = None,  # Comma-separated
    limit: int = Query(default=10, ge=1, le=50)
):
    """Search creators by performance metrics"""
    try:
        platform_list = None
        if platforms:
            platform_list = [platform.strip() for platform in platforms.split(",")]
        
        result = await search_service.search_by_performance_metrics(
            min_engagement_rate=min_engagement_rate,
            min_followers=min_followers,
            min_response_rate=min_response_rate,
            platforms=platform_list,
            limit=limit
        )
        return result
    except Exception as e:
        print(f"Performance search error: {e}")
        raise HTTPException(status_code=500, detail=f"Performance search failed: {str(e)}")

@app.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial query for suggestions"),
    limit: int = Query(default=5, ge=1, le=20)
):
    """Get search suggestions based on partial query"""
    try:
        suggestions = await search_service.get_search_suggestions(q, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"Search suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Search suggestions failed: {str(e)}")

@app.get("/statistics")
async def get_statistics():
    """Get creator database statistics"""
    try:
        stats = recommendation_service.get_creator_statistics()
        return stats
    except Exception as e:
        print(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")

@app.get("/creators/{creator_id}", response_model=CreatorRecommendation)
async def get_creator_details(creator_id: str):
    """Get detailed information about a specific creator"""
    try:
        creator_data = DEMO_CREATORS.get(creator_id)
        if not creator_data:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Convert to recommendation format
        from ..shared.utils import calculate_creator_score
        
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
            match_score=100.0,  # Perfect match with itself
            creator_score=calculate_creator_score(
                creator_data.get("engagement_rate", 0),
                creator_data.get("followers", 0),
                creator_data.get("response_rate", 50)
            ),
            language=creator_data.get("language", "English")
        )
        return recommendation
    except HTTPException:
        raise
    except Exception as e:
        print(f"Creator details error: {e}")
        raise HTTPException(status_code=500, detail=f"Creator details failed: {str(e)}")

@app.get("/debug/creators")
async def debug_list_creators():
    """Debug endpoint to list all available creators"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Debug endpoint not available")
    
    creators_summary = []
    for creator_id, creator_data in DEMO_CREATORS.items():
        creators_summary.append({
            "id": creator_id,
            "name": creator_data.get("name"),
            "platform": creator_data.get("platform"),
            "followers": creator_data.get("followers"),
            "categories": creator_data.get("categories", [])
        })
    
    return {
        "total_creators": len(DEMO_CREATORS),
        "creators": creators_summary
    }

@app.post("/debug/test-search")
async def debug_test_search(query: str = "fitness influencer"):
    """Debug endpoint to test search functionality"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Debug endpoint not available")
    
    try:
        request = CreatorSearchRequest(query=query, limit=5)
        result = await recommendation_service.search_creators(request)
        
        return {
            "query": query,
            "results_count": len(result.results),
            "search_time_ms": result.search_time_ms,
            "results": [
                {
                    "name": r.name,
                    "platform": r.platform,
                    "match_score": r.match_score,
                    "categories": r.categories
                }
                for r in result.results
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.creator_discovery_port,
        reload=settings.debug,
        log_level="info"
    )