from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import httpx
import re

from shared.database import get_db, Creator
from shared.config import settings

router = APIRouter()

CREATOR_DISCOVERY_URL = f"http://localhost:{settings.creator_discovery_port}"

@router.post("/search")
async def search_creators(search_request: Dict[str, Any], db: Session = Depends(get_db)):
    """Search creators with filters"""
    try:
        query_text = search_request.get('query', '').lower()
        
        # Extract location first
        location_match = None
        if 'from' in query_text:
            location_match = query_text.split('from')[-1].strip()
        
        # If we found a location, handle it directly
        if location_match:
            # Get all distinct locations
            locations_query = db.query(Creator.location).distinct()
            available_locations = [
                loc[0] for loc in locations_query.all() 
                if loc[0] and isinstance(loc[0], str)
            ]
            
            # Search for creators from this location
            creators = db.query(Creator).filter(
                Creator.location.ilike(f'%{location_match}%')
            ).all()
            
            # If no creators found, return helpful message
            if not creators:
                # Format available locations
                display_locations = sorted(list(set(available_locations)))[:5]
                locations_text = ", ".join(display_locations)
                if len(available_locations) > 5:
                    locations_text += f" and {len(available_locations) - 5} more"
                
                return {
                    "results": [],
                    "total_found": 0,
                    "query": query_text,
                    "search_time_ms": 0,
                    "used_cache": False,
                    "filters_applied": {"location": location_match},
                    "error_message": f"No creators found from {location_match}. Available locations include: {locations_text}"
                }
            
            # If creators found, return them
            results = []
            for creator in creators:
                results.append({
                    "creator_id": creator.id,
                    "name": creator.name,
                    "handle": creator.handle,
                    "platform": creator.platform,
                    "followers": creator.followers,
                    "engagement_rate": creator.engagement_rate,
                    "categories": creator.categories,
                    "location": creator.location,
                    "content_style": creator.content_style,
                    "demographics": creator.demographics,
                    "is_verified": creator.is_verified
                })
            
            return {
                "results": results,
                "total_found": len(results),
                "query": query_text,
                "search_time_ms": 0,
                "used_cache": False,
                "filters_applied": {"location": location_match}
            }
        
        # If no location in query, proceed with normal search
        # Apply filters if provided
        query = db.query(Creator)
        filters = search_request.get('filters', {})
        
        if filters:
            if platform := filters.get('platform'):
                query = query.filter(Creator.platform == platform)
            if min_followers := filters.get('min_followers'):
                query = query.filter(Creator.followers >= min_followers)
        
        # Get results
        creators = query.limit(50).all()
        
        # Format response
        results = []
        for creator in creators:
            results.append({
                "creator_id": creator.id,
                "name": creator.name,
                "handle": creator.handle,
                "platform": creator.platform,
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "categories": creator.categories,
                "location": creator.location,
                "content_style": creator.content_style,
                "demographics": creator.demographics,
                "is_verified": creator.is_verified
            })

        return {
            "results": results,
            "total_found": len(results),
            "query": query_text,
            "search_time_ms": 0,
            "used_cache": False,
            "filters_applied": filters
        }

    except Exception as e:
        print(f"Search error: {e}")
        return {
            "results": [],
            "total_found": 0,
            "query": query_text,
            "search_time_ms": 0,
            "used_cache": False,
            "error_message": str(e)
        }

@router.get("/{creator_id}")
async def get_creator(creator_id: str, db: Session = Depends(get_db)):
    """Get creator details by ID"""
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    return {
        "id": creator.id,
        "name": creator.name,
        "handle": creator.handle,
        "platform": creator.platform,
        "followers": creator.followers,
        "engagement_rate": creator.engagement_rate,
        "categories": creator.categories,
        "location": creator.location,
        "content_style": creator.content_style,
        "demographics": creator.demographics,
        "is_verified": creator.is_verified
    }
