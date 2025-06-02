# semantic search engine
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from .embeddings import GeminiEmbeddingEngine
import sys
from pathlib import Path
import json
import re

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.vector_store import vector_store
from shared.redis_client import redis_client
from shared.utils import Timer, calculate_creator_score
import asyncio

class SemanticSearchEngine:
    def __init__(self):
        self.embedding_engine = GeminiEmbeddingEngine()
        self.vector_store = vector_store
        
    async def search_creators(
        self,
        query: str,
        creators: Dict[str, Dict],
        top_k: int = 10,
        filters: Optional[Dict] = None,
        similarity_threshold: float = 0.3
    ) -> List[Dict]:
        """Perform semantic search for creators"""
        try:
            with Timer("Semantic creator search"):
                # Check cache first
                cache_key = f"{query}:{top_k}:{str(filters)}"
                cached_results = redis_client.get_cached_search_results(cache_key)
                if cached_results:
                    print("✅ Using cached search results")
                    return cached_results
                
                # Generate query embedding
                query_embedding = await self.embedding_engine.generate_single_embedding(query)
                if not query_embedding:
                    print("❌ Failed to generate query embedding")
                    return []
                
                # Get or generate creator embeddings
                creator_embeddings = await self._get_creator_embeddings(creators)
                
                # Perform similarity search
                similarities = self.vector_store.similarity_search(
                    query_embedding,
                    creator_embeddings,
                    top_k=top_k * 2,  # Get more to apply filters
                    similarity_threshold=similarity_threshold
                )
                
                # Apply filters and format results
                results = await self._format_search_results(
                    similarities, creators, filters, top_k
                )
                
                # Cache results
                redis_client.cache_search_results(cache_key, results)
                
                return results
                
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, creators, top_k, filters)
    
    async def _get_creator_embeddings(self, creators: Dict[str, Dict]) -> Dict[str, List[float]]:
        """Get embeddings for all creators (from database or generate if missing)"""
        embeddings = {}
        creators_to_embed = {}
        
        # First try to get embeddings from the creator data
        for creator_id, creator_data in creators.items():
            if creator_data.get('embedding'):
                try:
                    # Parse the embedding from string if needed
                    embedding = creator_data['embedding']
                    if isinstance(embedding, str):
                        embedding = json.loads(embedding)
                    embeddings[creator_id] = embedding
                    print(f"✅ Using existing embedding for creator {creator_id}")
                except Exception as e:
                    print(f"❌ Error parsing embedding for creator {creator_id}: {e}")
                    creators_to_embed[creator_id] = creator_data
            else:
                creators_to_embed[creator_id] = creator_data
        
        print(f"Found {len(embeddings)} existing embeddings")
        
        # Generate embeddings only for creators that don't have them
        if creators_to_embed:
            print(f"🔄 Generating embeddings for {len(creators_to_embed)} creators (missing embeddings)")
            new_embeddings = await self.embedding_engine.batch_generate_creator_embeddings(
                creators_to_embed
            )
            embeddings.update(new_embeddings)
        
        return embeddings
    
    async def _format_search_results(
        self,
        similarities: List[Tuple[str, float]],
        creators: Dict[str, Dict],
        filters: Optional[Dict],
        top_k: int
    ) -> List[Dict]:
        """Format and filter search results"""
        results = []
        
        for creator_id, similarity_score in similarities:
            creator_data = creators.get(creator_id)
            if not creator_data:
                continue
            
            # Apply filters
            if filters and not self._apply_filters(creator_data, filters):
                continue
            
            # Calculate additional scores
            creator_score = calculate_creator_score(
                creator_data.get('engagement_rate', 0),
                creator_data.get('followers', 0),
                creator_data.get('response_rate', 50)
            )
            
            # Format result
            result = {
                "creator_id": creator_id,
                "name": creator_data.get('name', ''),
                "handle": creator_data.get('handle', ''),
                "platform": creator_data.get('platform', ''),
                "followers": creator_data.get('followers', 0),
                "engagement_rate": creator_data.get('engagement_rate', 0),
                "categories": creator_data.get('categories', []),
                "demographics": creator_data.get('demographics', {}),
                "content_style": creator_data.get('content_style', ''),
                "location": creator_data.get('location', ''),
                "collaboration_rate": creator_data.get('collaboration_rate', ''),
                "response_rate": creator_data.get('response_rate', 0),
                "match_score": round(similarity_score * 100, 2),  # Convert to percentage
                "creator_score": creator_score,
                "language": creator_data.get('language', 'English')
            }
            
            results.append(result)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _parse_natural_language_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Parse natural language query to extract filters and clean query"""
        filters = {}
        clean_query = query.lower()
        
        # Extract location/country
        location_patterns = [
            r'from\s+(\w+)',
            r'in\s+(\w+)',
            r'(\w+)\s+influencers?'  # This will catch "nepal influencers"
        ]
        
        for pattern in location_patterns:
            if match := re.search(pattern, clean_query, re.IGNORECASE):
                location = match.group(1)
                if location not in ['show', 'me', 'the', 'all']:  # Skip common words
                    filters['location'] = location
                    clean_query = re.sub(pattern, '', clean_query).strip()
                    break
        
        # ... rest of the parsing code ...
        
        return clean_query, filters
    
    def _apply_filters(self, creator_data: Dict, filters: Dict) -> bool:
        """Apply filters to creator data"""
        try:
            # Platform filter
            if platform := filters.get('platform'):
                if creator_data.get('platform', '').lower() != platform.lower():
                    return False
            
            # Followers filters
            if min_followers := filters.get('min_followers'):
                if creator_data.get('followers', 0) < min_followers:
                    return False
            
            if max_followers := filters.get('max_followers'):
                if creator_data.get('followers', 0) > max_followers:
                    return False
            
            # Engagement rate filters
            if min_rate := filters.get('min_engagement_rate'):
                if creator_data.get('engagement_rate', 0) < min_rate:
                    return False
            
            if max_rate := filters.get('max_engagement_rate'):
                if creator_data.get('engagement_rate', 0) > max_rate:
                    return False
            
            # Categories filter
            if filter_categories := filters.get('categories'):
                creator_categories = set(c.lower() for c in creator_data.get('categories', []))
                if not any(c.lower() in creator_categories for c in filter_categories):
                    return False
            
            # Location filter
            if location := filters.get('location'):
                creator_location = creator_data.get('location', '').lower()
                # Check if location exists and matches (including partial matches)
                if not creator_location or location.lower() not in creator_location.lower():
                    return False
            
            return True
            
        except Exception as e:
            print(f"Filter application error: {e}")
            return True
    
    def _analyze_no_results(self, query: str, filters: Dict, creators: Dict[str, Dict]) -> str:
        """Analyze why no results were found and return a helpful message"""
        try:
            # Check for location filter
            if location := filters.get('location'):
                available_locations = set()
                for creator in creators.values():
                    if creator_location := creator.get('location'):
                        available_locations.add(creator_location.lower())
                
                if not available_locations:
                    return "No location information available for any creators"
                
                if location.lower() not in [loc.lower() for loc in available_locations]:
                    locations_list = sorted(list(available_locations))
                    # Only show up to 5 locations in the message
                    display_locations = locations_list[:5]
                    remaining = len(locations_list) - 5
                    locations_text = ", ".join(display_locations)
                    if remaining > 0:
                        locations_text += f" and {remaining} more"
                    return f"No creators found from {location}. Available locations include: {locations_text}"
            
            # ... rest of the analysis code ...
            
            return "No creators found matching your search criteria. Try adjusting your filters or search terms."
            
        except Exception as e:
            print(f"Error analyzing no results: {e}")
            return "No creators found matching your search criteria"
    
    def _fallback_search(
        self,
        query: str,
        creators: Dict[str, Dict],
        top_k: int,
        filters: Optional[Dict]
    ) -> List[Dict]:
        """Fallback keyword-based search when semantic search fails"""
        print("🔄 Using fallback keyword search")
        
        query_words = set(query.lower().split())
        results = []
        
        for creator_id, creator_data in creators.items():
            # Apply filters first
            if filters and not self._apply_filters(creator_data, filters):
                continue
            
            # Calculate keyword match score
            match_score = self._calculate_keyword_match(creator_data, query_words)
            
            if match_score > 0:
                result = {
                    "creator_id": creator_id,
                    "name": creator_data.get('name', ''),
                    "handle": creator_data.get('handle', ''),
                    "platform": creator_data.get('platform', ''),
                    "followers": creator_data.get('followers', 0),
                    "engagement_rate": creator_data.get('engagement_rate', 0),
                    "categories": creator_data.get('categories', []),
                    "demographics": creator_data.get('demographics', {}),
                    "content_style": creator_data.get('content_style', ''),
                    "location": creator_data.get('location', ''),
                    "collaboration_rate": creator_data.get('collaboration_rate', ''),
                    "response_rate": creator_data.get('response_rate', 0),
                    "match_score": match_score,
                    "creator_score": calculate_creator_score(
                        creator_data.get('engagement_rate', 0),
                        creator_data.get('followers', 0),
                        creator_data.get('response_rate', 50)
                    ),
                    "language": creator_data.get('language', 'English')
                }
                results.append(result)
        
        # Sort by match score and return top_k
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:top_k]
    
    def _calculate_keyword_match(self, creator_data: Dict, query_words: set) -> float:
        """Calculate keyword match score for fallback search"""
        score = 0.0
        total_words = len(query_words)
        
        if total_words == 0:
            return 0.0
        
        # Check categories
        categories = creator_data.get('categories', [])
        category_words = set(' '.join(categories).lower().split())
        category_matches = len(query_words.intersection(category_words))
        score += (category_matches / total_words) * 40  # 40 points max for categories
        
        # Check content style
        content_style = creator_data.get('content_style', '').lower()
        content_words = set(content_style.split())
        content_matches = len(query_words.intersection(content_words))
        score += (content_matches / total_words) * 30  # 30 points max for content
        
        # Check name
        name = creator_data.get('name', '').lower()
        name_words = set(name.split())
        name_matches = len(query_words.intersection(name_words))
        score += (name_matches / total_words) * 20  # 20 points max for name
        
        # Check platform
        platform = creator_data.get('platform', '').lower()
        if platform in query_words:
            score += 10  # 10 points for platform match
        
        return min(score, 100.0)  # Cap at 100
    
    async def get_recommendations(
        self,
        creator_id: str,
        creators: Dict[str, Dict],
        count: int = 5
    ) -> List[Dict]:
        """Get similar creators based on a reference creator"""
        try:
            reference_creator = creators.get(creator_id)
            if not reference_creator:
                return []
            
            # Create query from reference creator
            query = self.embedding_engine._create_creator_text(reference_creator)
            
            # Search for similar creators (excluding the reference)
            results = await self.search_creators(query, creators, top_k=count + 1)
            
            # Remove the reference creator from results
            return [r for r in results if r['creator_id'] != creator_id][:count]
            
        except Exception as e:
            print(f"Recommendation error: {e}")
            return []