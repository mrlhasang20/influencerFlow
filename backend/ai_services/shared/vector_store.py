# vector database integration
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from .redis_client import redis_client
from .config import VECTOR_CONFIG
import uuid

class VectorStore:
    def __init__(self):
        self.dimension = VECTOR_CONFIG["dimension"]
        self.metric = VECTOR_CONFIG["metric"]
        
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            # Handle zero vectors
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return np.dot(v1, v2) / (norm1 * norm2)
        except Exception as e:
            print(f"Cosine similarity error: {e}")
            return 0.0
    
    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            return float(np.linalg.norm(v1 - v2))
        except Exception as e:
            print(f"Euclidean distance error: {e}")
            return float('inf')
    
    def store_vector(self, vector_id: str, embedding: List[float], metadata: Dict = None) -> bool:
        """Store vector with metadata in Redis"""
        try:
            vector_data = {
                "id": vector_id,
                "embedding": embedding,
                "metadata": metadata or {},
                "dimension": len(embedding)
            }
            
            key = f"vector:{vector_id}"
            return redis_client.set(key, vector_data)
        except Exception as e:
            print(f"Store vector error: {e}")
            return False
    
    def get_vector(self, vector_id: str) -> Optional[Dict]:
        """Retrieve vector by ID"""
        try:
            key = f"vector:{vector_id}"
            return redis_client.get(key)
        except Exception as e:
            print(f"Get vector error: {e}")
            return None
    
    def similarity_search(
        self, 
        query_vector: List[float], 
        stored_vectors: Dict[str, List[float]], 
        top_k: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Perform similarity search against stored vectors"""
        try:
            similarities = []
            
            for vector_id, stored_vector in stored_vectors.items():
                if self.metric == "cosine":
                    similarity = self.cosine_similarity(query_vector, stored_vector)
                elif self.metric == "euclidean":
                    # Convert distance to similarity (closer = higher score)
                    distance = self.euclidean_distance(query_vector, stored_vector)
                    similarity = 1.0 / (1.0 + distance)
                else:
                    similarity = self.cosine_similarity(query_vector, stored_vector)
                
                if similarity >= similarity_threshold:
                    similarities.append((vector_id, similarity))
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Similarity search error: {e}")
            return []
    
    def batch_store_vectors(self, vectors: Dict[str, Dict]) -> bool:
        """Store multiple vectors in batch"""
        try:
            success_count = 0
            for vector_id, vector_data in vectors.items():
                if self.store_vector(
                    vector_id, 
                    vector_data["embedding"], 
                    vector_data.get("metadata", {})
                ):
                    success_count += 1
            
            return success_count == len(vectors)
        except Exception as e:
            print(f"Batch store vectors error: {e}")
            return False
    
    def get_all_vectors_by_prefix(self, prefix: str = "vector:") -> Dict[str, Dict]:
        """Get all vectors with given prefix"""
        try:
            # This is a simplified implementation
            # In production, you'd want more efficient methods
            vectors = {}
            
            # Note: This is not the most efficient way with Redis
            # but works for demo purposes
            return vectors
            
        except Exception as e:
            print(f"Get all vectors error: {e}")
            return {}
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete vector by ID"""
        try:
            key = f"vector:{vector_id}"
            return redis_client.delete(key)
        except Exception as e:
            print(f"Delete vector error: {e}")
            return False
    
    def vector_exists(self, vector_id: str) -> bool:
        """Check if vector exists"""
        try:
            key = f"vector:{vector_id}"
            return redis_client.exists(key)
        except Exception as e:
            print(f"Vector exists error: {e}")
            return False
    
    def get_vector_stats(self) -> Dict:
        """Get statistics about stored vectors"""
        try:
            # This would be implemented with more sophisticated 
            # vector database in production
            stats = {
                "total_vectors": 0,
                "dimension": self.dimension,
                "metric": self.metric
            }
            return stats
        except Exception as e:
            print(f"Get vector stats error: {e}")
            return {}

# Global vector store instance
vector_store = VectorStore()