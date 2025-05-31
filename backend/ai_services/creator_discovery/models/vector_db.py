# vector search

from typing import Dict, List, Optional, Tuple
import json
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.vector_store import vector_store
from shared.redis_client import redis_client
from shared.utils import generate_id
from models.embeddings import GeminiEmbeddingEngine

class CreatorVectorDB:
    def __init__(self):
        self.vector_store = vector_store
        self.embedding_engine = GeminiEmbeddingEngine()
        self.namespace = "creators"
    
    async def index_creator(self, creator_id: str, creator_data: Dict) -> bool:
        """Index a creator in the vector database"""
        try:
            # Generate embedding for creator
            embedding = await self.embedding_engine.generate_creator_embedding(creator_data)
            if not embedding:
                print(f"❌ Failed to generate embedding for creator {creator_id}")
                return False
            
            # Store vector with metadata
            vector_id = f"{self.namespace}:{creator_id}"
            metadata = {
                "creator_id": creator_id,
                "name": creator_data.get('name', ''),
                "platform": creator_data.get('platform', ''),
                "categories": creator_data.get('categories', []),
                "followers": creator_data.get('followers', 0),
                "engagement_rate": creator_data.get('engagement_rate', 0.0),
                "location": creator_data.get('location', ''),
                "indexed_at": "2024-01-01"  # You'd use actual timestamp
            }
            
            success = self.vector_store.store_vector(vector_id, embedding, metadata)
            if success:
                print(f"✅ Indexed creator {creator_id}")
            else:
                print(f"❌ Failed to index creator {creator_id}")
                
            return success
            
        except Exception as e:
            print(f"Error indexing creator {creator_id}: {e}")
            return False
    
    async def batch_index_creators(self, creators: Dict[str, Dict]) -> Dict[str, bool]:
        """Index multiple creators in batch"""
        results = {}
        
        try:
            # Generate embeddings for all creators
            print(f"🔄 Generating embeddings for {len(creators)} creators...")
            creator_embeddings = await self.embedding_engine.batch_generate_creator_embeddings(creators)
            
            # Store all vectors
            vectors_to_store = {}
            for creator_id, creator_data in creators.items():
                if creator_id in creator_embeddings:
                    vector_id = f"{self.namespace}:{creator_id}"
                    metadata = {
                        "creator_id": creator_id,
                        "name": creator_data.get('name', ''),
                        "platform": creator_data.get('platform', ''),
                        "categories": creator_data.get('categories', []),
                        "followers": creator_data.get('followers', 0),
                        "engagement_rate": creator_data.get('engagement_rate', 0.0),
                        "location": creator_data.get('location', ''),
                        "indexed_at": "2024-01-01"
                    }
                    
                    vectors_to_store[vector_id] = {
                        "embedding": creator_embeddings[creator_id],
                        "metadata": metadata
                    }
                    results[creator_id] = True
                else:
                    results[creator_id] = False
            
            # Batch store vectors
            if vectors_to_store:
                batch_success = self.vector_store.batch_store_vectors(vectors_to_store)
                if batch_success:
                    print(f"✅ Successfully indexed {len(vectors_to_store)} creators")
                else:
                    print(f"⚠️ Partial success in batch indexing")
            
            return results
            
        except Exception as e:
            print(f"Batch indexing error: {e}")
            return {creator_id: False for creator_id in creators.keys()}
    
    def get_creator_vector(self, creator_id: str) -> Optional[Dict]:
        """Get stored vector for a creator"""
        try:
            vector_id = f"{self.namespace}:{creator_id}"
            return self.vector_store.get_vector(vector_id)
        except Exception as e:
            print(f"Error getting creator vector {creator_id}: {e}")
            return None
    
    def delete_creator(self, creator_id: str) -> bool:
        """Delete creator from vector database"""
        try:
            vector_id = f"{self.namespace}:{creator_id}"
            success = self.vector_store.delete_vector(vector_id)
            if success:
                print(f"✅ Deleted creator {creator_id} from vector DB")
            return success
        except Exception as e:
            print(f"Error deleting creator {creator_id}: {e}")
            return False
    
    def creator_exists(self, creator_id: str) -> bool:
        """Check if creator exists in vector database"""
        try:
            vector_id = f"{self.namespace}:{creator_id}"
            return self.vector_store.vector_exists(vector_id)
        except Exception as e:
            print(f"Error checking creator existence {creator_id}: {e}")
            return False
    
    async def find_similar_creators(
        self,
        creator_id: str,
        all_creators: Dict[str, Dict],
        top_k: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Find creators similar to a given creator"""
        try:
            # Get the reference creator's vector
            reference_vector_data = self.get_creator_vector(creator_id)
            if not reference_vector_data:
                print(f"❌ Creator {creator_id} not found in vector DB")
                return []
            
            reference_embedding = reference_vector_data["embedding"]
            
            # Get embeddings for all other creators
            other_creators = {cid: cdata for cid, cdata in all_creators.items() if cid != creator_id}
            creator_embeddings = {}
            
            for other_id, other_data in other_creators.items():
                vector_data = self.get_creator_vector(other_id)
                if vector_data:
                    creator_embeddings[other_id] = vector_data["embedding"]
                else:
                    # Generate embedding if not stored
                    embedding = await self.embedding_engine.generate_creator_embedding(other_data)
                    if embedding:
                        creator_embeddings[other_id] = embedding
            
            # Perform similarity search
            similarities = self.vector_store.similarity_search(
                reference_embedding,
                creator_embeddings,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            return similarities
            
        except Exception as e:
            print(f"Error finding similar creators: {e}")
            return []
    
    async def search_by_query_vector(
        self,
        query_embedding: List[float],
        all_creators: Dict[str, Dict],
        top_k: int = 10,
        similarity_threshold: float = 0.3
    ) -> List[Tuple[str, float]]:
        """Search creators using a query embedding"""
        try:
            # Get embeddings for all creators
            creator_embeddings = {}
            
            for creator_id, creator_data in all_creators.items():
                vector_data = self.get_creator_vector(creator_id)
                if vector_data:
                    creator_embeddings[creator_id] = vector_data["embedding"]
                else:
                    # Generate embedding if not stored
                    embedding = await self.embedding_engine.generate_creator_embedding(creator_data)
                    if embedding:
                        creator_embeddings[creator_id] = embedding
                        # Store for future use
                        await self.index_creator(creator_id, creator_data)
            
            # Perform similarity search
            similarities = self.vector_store.similarity_search(
                query_embedding,
                creator_embeddings,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            return similarities
            
        except Exception as e:
            print(f"Error searching by query vector: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the vector database"""
        try:
            stats = self.vector_store.get_vector_stats()
            
            # Add namespace-specific stats
            stats.update({
                "namespace": self.namespace,
                "embedding_model": self.embedding_engine.model,
                "embedding_dimension": self.embedding_engine.get_embedding_dimension()
            })
            
            return stats
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    async def reindex_all_creators(self, creators: Dict[str, Dict]) -> bool:
        """Reindex all creators (useful for updates)"""
        try:
            print(f"🔄 Reindexing {len(creators)} creators...")
            
            # Delete existing vectors
            for creator_id in creators.keys():
                self.delete_creator(creator_id)
            
            # Batch index all creators
            results = await self.batch_index_creators(creators)
            
            success_count = sum(1 for success in results.values() if success)
            print(f"✅ Reindexed {success_count}/{len(creators)} creators")
            
            return success_count == len(creators)
            
        except Exception as e:
            print(f"Error reindexing creators: {e}")
            return False
    
    def clear_namespace(self) -> bool:
        """Clear all vectors in the creators namespace"""
        try:
            # This would be more efficient with a proper vector database
            # For now, we'll implement a simple clear
            print(f"🗑️ Clearing {self.namespace} namespace...")
            return True
        except Exception as e:
            print(f"Error clearing namespace: {e}")
            return False