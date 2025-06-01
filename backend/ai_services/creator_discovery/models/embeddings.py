# gemini embeddings
import google.generativeai as genai
from typing import List, Dict, Optional
import asyncio
import sys
from pathlib import Path
import json

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.redis_client import redis_client
from shared.utils import retry_async, Timer
import time
from shared.database import get_db_session, Creator

class GeminiEmbeddingEngine:
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.gemini_embedding_model
        self.cache_enabled = True
        
    @retry_async(max_retries=3, delay=1.0)
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using Gemini"""
        if not texts:
            return []
            
        embeddings = []
        
        for text in texts:
            # Check cache first
            if self.cache_enabled:
                cached_embedding = await redis_client.get_cached_embedding_async(text)
                if cached_embedding:
                    embeddings.append(cached_embedding)
                    continue
            
            try:
                # Generate embedding using Gemini
                with Timer(f"Embedding generation for text of length {len(text)}"):
                    result = genai.embed_content(
                        model=f"models/{self.model}",
                        content=text,
                        task_type="semantic_similarity"
                    )
                    
                    embedding = result['embedding']
                    embeddings.append(embedding)
                    
                    # Cache the embedding
                    if self.cache_enabled:
                        await redis_client.cache_embedding_async(text, embedding)
                        
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error generating embedding for text: {e}")
                # Return zero vector as fallback
                embeddings.append([0.0] * 768)  # text-embedding-004 dimension
                
        return embeddings
    
    async def generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else None
    
    async def generate_creator_embedding(self, creator_data: Dict) -> Optional[List[float]]:
        """Generate comprehensive embedding for a creator profile"""
        try:
            # Create comprehensive text representation of creator
            creator_text = self._create_creator_text(creator_data)
            return await self.generate_single_embedding(creator_text)
        except Exception as e:
            print(f"Error generating creator embedding: {e}")
            return None
    
    def _create_creator_text(self, creator_data: Dict) -> str:
        """Create comprehensive text representation of creator for embedding"""
        text_parts = []
        
        # Basic info
        if creator_data.get('name'):
            text_parts.append(f"Creator name: {creator_data['name']}")
        
        if creator_data.get('platform'):
            text_parts.append(f"Platform: {creator_data['platform']}")
            
        # Content and style
        if creator_data.get('content_style'):
            text_parts.append(f"Content style: {creator_data['content_style']}")
            
        if creator_data.get('categories'):
            categories = ', '.join(creator_data['categories'])
            text_parts.append(f"Content categories: {categories}")
            
        # Audience info
        if creator_data.get('demographics'):
            demo = creator_data['demographics']
            if demo.get('age_group'):
                text_parts.append(f"Target audience age: {demo['age_group']}")
            if demo.get('gender_split'):
                gender_info = ', '.join([f"{k}: {v}%" for k, v in demo['gender_split'].items()])
                text_parts.append(f"Audience gender split: {gender_info}")
            if demo.get('top_locations'):
                locations = ', '.join(demo['top_locations'])
                text_parts.append(f"Audience locations: {locations}")
        
        # Performance metrics
        if creator_data.get('followers'):
            text_parts.append(f"Follower count: {creator_data['followers']}")
            
        if creator_data.get('engagement_rate'):
            text_parts.append(f"Engagement rate: {creator_data['engagement_rate']}%")
            
        # Language and location
        if creator_data.get('language'):
            text_parts.append(f"Content language: {creator_data['language']}")
            
        if creator_data.get('location'):
            text_parts.append(f"Creator location: {creator_data['location']}")
            
        return '. '.join(text_parts)
    
    async def batch_generate_creator_embeddings(self, creators: Dict[str, Dict]) -> Dict[str, List[float]]:
        """Generate embeddings for multiple creators in batch"""
        embeddings = {}
        
        # Prepare texts for all creators
        creator_texts = []
        creator_ids = []
        
        for creator_id, creator_data in creators.items():
            creator_text = self._create_creator_text(creator_data)
            creator_texts.append(creator_text)
            creator_ids.append(creator_id)
        
        # Generate embeddings in batch
        embedding_results = await self.generate_embeddings(creator_texts)
        
        # Map embeddings back to creator IDs
        for creator_id, embedding in zip(creator_ids, embedding_results):
            embeddings[creator_id] = embedding
            
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        return 768  # text-embedding-004 produces 768-dimensional vectors
    
    async def get_or_generate_creator_embedding(self, creator_id: str, creator_data: Dict) -> Optional[List[float]]:
        """Get embedding from database or generate if not exists"""
        session = get_db_session()
        try:
            creator = session.query(Creator).filter(Creator.id == creator_id).first()
            if creator and creator.embedding:
                # If embedding exists in database, use it
                return json.loads(creator.embedding)
            else:
                # Generate new embedding
                embedding = await self.generate_creator_embedding(creator_data)
                if embedding and creator:
                    # Store in database for future use
                    creator.embedding = json.dumps(embedding)
                    session.commit()
                return embedding
        except Exception as e:
            print(f"Error getting/generating creator embedding: {e}")
            return None
        finally:
            session.close()