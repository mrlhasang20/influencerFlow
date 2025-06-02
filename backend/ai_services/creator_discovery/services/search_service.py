# advanced search service
from typing import List, Dict, Optional, Any
import asyncio
import time
from models.search_engine import SemanticSearchEngine
from schemas.creator_schemas import (
    CreatorSearchRequest, CreatorSearchResponse, CreatorRecommendation,
    BatchSearchRequest, BatchSearchResponse, SearchFilters
)

import sys
from pathlib import Path
import json

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.config import DEMO_CREATORS
from shared.utils import Timer, calculate_creator_score
from shared.redis_client import redis_client
from sqlalchemy.orm import Session
from models.creator_model import Creator

class CreatorSearchService:
    def __init__(self):
        self.search_engine = SemanticSearchEngine()
    
    async def advanced_search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
        db: Session = None
    ) -> CreatorSearchResponse:
        """Perform advanced search with comprehensive filtering"""
        start_time = time.time()
        
        try:
            with Timer(f"Advanced search for: '{query}'"):
                # Query real database and convert to dictionary
                creators_list = db.query(Creator).all()
                creators = {}
                
                print(f"Found {len(creators_list)} creators in database")
                
                # Early check for empty database
                if not creators_list:
                    return CreatorSearchResponse(
                        results=[],
                        total_found=0,
                        query=query,
                        search_time_ms=0,
                        used_cache=False,
                        filters_applied=None,
                        error_message="No creators found in the database"
                    )
                
                # Convert creators to dictionary format
                for creator in creators_list:
                    # Convert embedding from string to list if it exists
                    embedding = None
                    if creator.embedding:
                        try:
                            if isinstance(creator.embedding, str):
                                embedding = json.loads(creator.embedding)
                            else:
                                embedding = creator.embedding
                            print(f"✅ Successfully loaded embedding for creator {creator.id}")
                        except Exception as e:
                            print(f"❌ Failed to parse embedding for creator {creator.id}: {e}")
                    
                    creators[creator.id] = {
                        'id': creator.id,
                        'name': creator.name,
                        'handle': creator.handle,
                        'platform': creator.platform,
                        'followers': creator.followers,
                        'engagement_rate': creator.engagement_rate,
                        'categories': creator.categories if isinstance(creator.categories, list) else [],
                        'demographics': creator.demographics if isinstance(creator.demographics, dict) else {},
                        'content_style': creator.content_style,
                        'language': creator.language,
                        'location': creator.location,
                        'collaboration_rate': creator.collaboration_rate,
                        'response_rate': creator.response_rate,
                        'embedding': embedding,
                        'is_verified': creator.is_verified
                    }
                
                # Convert SearchFilters to dict for the search engine
                filter_dict = {}
                if filters:
                    if filters.platform:
                        filter_dict["platform"] = filters.platform
                    if filters.min_followers is not None:
                        filter_dict["min_followers"] = filters.min_followers
                    if filters.max_followers is not None:
                        filter_dict["max_followers"] = filters.max_followers
                    if filters.min_engagement_rate is not None:
                        filter_dict["min_engagement_rate"] = filters.min_engagement_rate
                    if filters.max_engagement_rate is not None:
                        filter_dict["max_engagement_rate"] = filters.max_engagement_rate
                    if filters.categories:
                        filter_dict["categories"] = filters.categories
                    if filters.location:
                        filter_dict["location"] = filters.location
                    if filters.language:
                        filter_dict["language"] = filters.language
                    if filters.age_group:
                        filter_dict["age_group"] = filters.age_group
                    if filters.response_rate_min is not None:
                        filter_dict["response_rate_min"] = filters.response_rate_min
                
                print(f"Applying filters: {filter_dict}")
                
                # Perform semantic search
                search_results = await self.search_engine.search_creators(
                    query=query,
                    creators=creators,
                    top_k=limit,
                    filters=filter_dict,
                    similarity_threshold=0.2
                )
                
                # If no results, analyze why
                if not search_results:
                    error_message = self._analyze_no_results(query, filter_dict, creators)
                    return CreatorSearchResponse(
                        results=[],
                        total_found=0,
                        query=query,
                        search_time_ms=(time.time() - start_time) * 1000,
                        used_cache=False,
                        filters_applied=filter_dict,
                        error_message=error_message
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
                
                search_time = (time.time() - start_time) * 1000
                
                return CreatorSearchResponse(
                    results=recommendations,
                    total_found=len(recommendations),
                    query=query,
                    search_time_ms=search_time,
                    used_cache=False,
                    filters_applied=filter_dict if filter_dict else None
                )
                
        except Exception as e:
            print(f"Advanced search error: {e}")
            import traceback
            traceback.print_exc()
            return CreatorSearchResponse(
                results=[],
                total_found=0,
                query=query,
                search_time_ms=(time.time() - start_time) * 1000,
                error_message=f"Search failed: {str(e)}"
            )
    
    def _analyze_no_results(self, query: str, filters: Dict, creators: Dict) -> str:
        """Analyze why no results were found and return a helpful message"""
        try:
            # Check for location filter
            if location := filters.get('location'):
                available_locations = set()
                for creator in creators.values():
                    if creator_location := creator.get('location'):
                        available_locations.add(creator_location.lower())
                
                if location.lower() not in available_locations:
                    return f"No creators found from {location}. Available locations are: {', '.join(sorted(available_locations))}"
            
            # Check for category filter
            if categories := filters.get('categories'):
                available_categories = set()
                for creator in creators.values():
                    available_categories.update(c.lower() for c in creator.get('categories', []))
                
                missing_categories = [c for c in categories if c.lower() not in available_categories]
                if missing_categories:
                    return f"No creators found in categories: {', '.join(missing_categories)}. Available categories are: {', '.join(sorted(available_categories))}"
            
            # Check for follower count filter
            if min_followers := filters.get('min_followers'):
                max_available = max(c.get('followers', 0) for c in creators.values())
                if min_followers > max_available:
                    return f"No creators found with {min_followers:,} or more followers. Maximum available is {max_available:,} followers"
            
            # Check for engagement rate filter
            if min_rate := filters.get('min_engagement_rate'):
                max_rate = max(c.get('engagement_rate', 0) for c in creators.values())
                if min_rate > max_rate:
                    return f"No creators found with {min_rate}% or higher engagement rate. Maximum available is {max_rate}%"
            
            # Generic message if no specific reason found
            return "No creators found matching your search criteria. Try adjusting your filters or search terms."
            
        except Exception as e:
            print(f"Error analyzing no results: {e}")
            return "No creators found matching your search criteria"
    
    async def batch_search(self, request: BatchSearchRequest) -> BatchSearchResponse:
        """Perform batch search for multiple queries"""
        start_time = time.time()
        
        try:
            results = {}
            
            # Process each query
            for query in request.queries:
                # Create search request
                search_request = CreatorSearchRequest(
                    query=query,
                    limit=request.limit_per_query,
                    filters=request.common_filters.dict() if request.common_filters else None
                )
                
                # Perform search
                search_result = await self.advanced_search(
                    query=query,
                    filters=request.common_filters,
                    limit=request.limit_per_query
                )
                
                results[query] = search_result
            
            processing_time = (time.time() - start_time) * 1000
            
            return BatchSearchResponse(
                results=results,
                total_queries=len(request.queries),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            print(f"Batch search error: {e}")
            return BatchSearchResponse(
                results={},
                total_queries=len(request.queries),
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    async def search_by_audience_demographics(
        self,
        target_age_group: str,
        target_gender: Optional[str] = None,
        target_locations: Optional[List[str]] = None,
        limit: int = 10,
        db: Session = None
    ) -> List[CreatorRecommendation]:
        """Search creators by audience demographics"""
        try:
            matching_creators = []
            
            # Query creators with matching demographics from DB
            creators = db.query(Creator).filter(
                Creator.demographics['age_group'].astext == target_age_group
            ).all()
            
            for creator_id, creator_data in self.creators_data.items():
                demographics = creator_data.get("demographics", {})
                
                # Check age group match
                creator_age_group = demographics.get("age_group", "")
                if target_age_group not in creator_age_group:
                    continue
                
                # Check gender distribution if specified
                if target_gender:
                    gender_split = demographics.get("gender_split", {})
                    target_percentage = gender_split.get(target_gender.lower(), 0)
                    if target_percentage < 60:  # Require majority audience
                        continue
                
                # Check location overlap if specified
                if target_locations:
                    creator_locations = demographics.get("top_locations", [])
                    if not any(loc in creator_locations for loc in target_locations):
                        continue
                
                # Calculate demographic match score
                match_score = self._calculate_demographic_match_score(
                    demographics, target_age_group, target_gender, target_locations
                )
                
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
                    match_score=match_score,
                    creator_score=calculate_creator_score(
                        creator_data.get("engagement_rate", 0),
                        creator_data.get("followers", 0),
                        creator_data.get("response_rate", 50)
                    ),
                    language=creator_data.get("language", "English")
                )
                matching_creators.append(recommendation)
            
            # Sort by match score and return top results
            matching_creators.sort(key=lambda x: x.match_score, reverse=True)
            return matching_creators[:limit]
            
        except Exception as e:
            print(f"Demographic search error: {e}")
            return []
    
    def _calculate_demographic_match_score(
        self,
        demographics: Dict,
        target_age_group: str,
        target_gender: Optional[str],
        target_locations: Optional[List[str]]
    ) -> float:
        """Calculate demographic match score"""
        score = 0.0
        
        # Age group match (40 points)
        creator_age_group = demographics.get("age_group", "")
        if target_age_group in creator_age_group:
            score += 40
        
        # Gender match (30 points)
        if target_gender:
            gender_split = demographics.get("gender_split", {})
            target_percentage = gender_split.get(target_gender.lower(), 0)
            score += min(target_percentage / 100 * 30, 30)
        else:
            score += 30  # Full points if gender not specified
        
        # Location match (30 points)
        if target_locations:
            creator_locations = demographics.get("top_locations", [])
            matches = sum(1 for loc in target_locations if loc in creator_locations)
            score += min(matches / len(target_locations) * 30, 30)
        else:
            score += 30  # Full points if location not specified
        
        return min(score, 100.0)
    
    async def search_by_performance_metrics(
        self,
        min_engagement_rate: float,
        min_followers: int,
        min_response_rate: Optional[int] = None,
        platforms: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[CreatorRecommendation]:
        """Search creators by performance metrics"""
        try:
            matching_creators = []
            
            for creator_id, creator_data in self.creators_data.items():
                # Check engagement rate
                if creator_data.get("engagement_rate", 0) < min_engagement_rate:
                    continue
                
                # Check follower count
                if creator_data.get("followers", 0) < min_followers:
                    continue
                
                # Check response rate
                if min_response_rate is not None:
                    if creator_data.get("response_rate", 0) < min_response_rate:
                        continue
                
                # Check platform
                if platforms:
                    if creator_data.get("platform", "") not in platforms:
                        continue
                
                # Calculate performance score
                performance_score = self._calculate_performance_score(creator_data)
                
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
                    match_score=performance_score,
                    creator_score=calculate_creator_score(
                        creator_data.get("engagement_rate", 0),
                        creator_data.get("followers", 0),
                        creator_data.get("response_rate", 50)
                    ),
                    language=creator_data.get("language", "English")
                )
                matching_creators.append(recommendation)
            
            # Sort by performance score
            matching_creators.sort(key=lambda x: x.match_score, reverse=True)
            return matching_creators[:limit]
            
        except Exception as e:
            print(f"Performance search error: {e}")
            return []
    
    def _calculate_performance_score(self, creator_data: Dict) -> float:
        """Calculate performance-based score"""
        engagement_rate = creator_data.get("engagement_rate", 0)
        followers = creator_data.get("followers", 0)
        response_rate = creator_data.get("response_rate", 50)
        
        # Normalize scores
        engagement_score = min(engagement_rate / 10 * 40, 40)  # Max 40 points
        
        # Logarithmic scaling for followers
        import math
        follower_score = min(math.log10(max(followers, 1)) * 8, 40)  # Max 40 points
        
        response_score = response_rate / 100 * 20  # Max 20 points
        
        return engagement_score + follower_score + response_score
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            suggestions = set()
            partial_lower = partial_query.lower()
            
            # Get suggestions from creator categories
            for creator_data in self.creators_data.values():
                for category in creator_data.get("categories", []):
                    if partial_lower in category.lower():
                        suggestions.add(category)
                
                # Get suggestions from content style
                content_style = creator_data.get("content_style", "")
                if partial_lower in content_style.lower():
                    # Extract meaningful phrases
                    words = content_style.split()
                    for i, word in enumerate(words):
                        if partial_lower in word.lower():
                            if i < len(words) - 1:
                                suggestions.add(f"{word} {words[i+1]}")
                            suggestions.add(word)
                
                # Get suggestions from platform
                platform = creator_data.get("platform", "")
                if partial_lower in platform.lower():
                    suggestions.add(platform)
            
            # Common search terms
            common_terms = [
                "fitness influencers", "tech reviewers", "fashion bloggers",
                "food creators", "gaming streamers", "beauty gurus",
                "travel influencers", "lifestyle creators", "educational content",
                "comedy creators", "music artists", "art creators"
            ]
            
            for term in common_terms:
                if partial_lower in term.lower():
                    suggestions.add(term)
            
            return list(suggestions)[:limit]
            
        except Exception as e:
            print(f"Search suggestions error: {e}")
            return []