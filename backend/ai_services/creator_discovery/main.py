from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
import uvicorn

app = FastAPI(title="Creator Discovery Service")

# Mock data for demo
MOCK_CREATORS = {
    "fitness_jane": {
        "id": "fitness_jane",
        "name": "Jane Fitness",
        "platform": "Instagram", 
        "followers": 150000,
        "engagement_rate": 4.2,
        "categories": ["fitness", "health", "wellness"],
        "description": "Fitness trainer specializing in HIIT workouts and nutrition coaching",
        "location": "United States",
        "avg_likes": 6300,
        "content_type": "Workout videos, nutrition tips, motivational posts"
    },
    "tech_alex": {
        "id": "tech_alex",
        "name": "Alex TechReviews", 
        "platform": "YouTube",
        "followers": 300000,
        "engagement_rate": 6.8,
        "categories": ["technology", "reviews", "gadgets"],
        "description": "Tech enthusiast reviewing latest gadgets and software",
        "location": "Canada",
        "avg_likes": 20400,
        "content_type": "Product reviews, tech tutorials, unboxing videos"
    },
    "beauty_sarah": {
        "id": "beauty_sarah",
        "name": "Sarah Beauty",
        "platform": "TikTok",
        "followers": 450000, 
        "engagement_rate": 8.5,
        "categories": ["beauty", "skincare", "makeup"],
        "description": "Beauty influencer with focus on skincare routines and makeup tutorials",
        "location": "United Kingdom",
        "avg_likes": 38250,
        "content_type": "Makeup tutorials, skincare routines, product reviews"
    },
    "travel_mike": {
        "id": "travel_mike",
        "name": "Mike Adventures",
        "platform": "Instagram",
        "followers": 200000,
        "engagement_rate": 5.3,
        "categories": ["travel", "adventure", "photography"],
        "description": "Adventure travel photographer documenting unique destinations",
        "location": "Australia", 
        "avg_likes": 10600,
        "content_type": "Travel photography, destination guides, adventure vlogs"
    }
}

class CreatorSearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_followers: Optional[int] = None
    platform: Optional[str] = None

class CreatorProfile(BaseModel):
    id: str
    name: str
    platform: str
    followers: int
    engagement_rate: float
    categories: List[str]
    description: str
    location: str
    match_score: float = 0.0

@app.post("/search", response_model=List[CreatorProfile])
async def search_creators(request: CreatorSearchRequest):
    """Search for creators using simple keyword matching (MVP version)"""
    results = []
    query_lower = request.query.lower()
    
    for creator_id, creator in MOCK_CREATORS.items():
        # Simple scoring based on keyword matches
        score = 0.0
        
        # Check categories
        for category in creator['categories']:
            if category in query_lower:
                score += 0.3
                
        # Check description
        if any(word in creator['description'].lower() for word in query_lower.split()):
            score += 0.4
            
        # Check platform match
        if request.platform and request.platform.lower() == creator['platform'].lower():
            score += 0.2
            
        # Check follower count
        if request.min_followers and creator['followers'] >= request.min_followers:
            score += 0.1
            
        if score > 0:
            results.append(CreatorProfile(
                id=creator['id'],
                name=creator['name'],
                platform=creator['platform'],
                followers=creator['followers'],
                engagement_rate=creator['engagement_rate'],
                categories=creator['categories'],
                description=creator['description'],
                location=creator['location'],
                match_score=score
            ))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x.match_score, reverse=True)
    return results[:request.limit]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "creator-discovery"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
