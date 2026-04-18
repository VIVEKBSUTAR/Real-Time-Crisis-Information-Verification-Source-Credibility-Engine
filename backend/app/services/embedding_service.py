import numpy as np
from typing import List
import uuid
import asyncio
from app.core.config import settings

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL_LOADED = True
except ImportError:
    EMBEDDING_MODEL_LOADED = False

class EmbeddingService:
    """Handles embedding generation and clustering"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model lazily"""
        if EMBEDDING_MODEL_LOADED:
            try:
                self.model = SentenceTransformer(self.model_name)
                print(f"✅ Embedding model loaded: {self.model_name}")
            except Exception as e:
                print(f"⚠️ Could not load embedding model: {e}")
                self.model = None
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        if not self.model:
            # Mock embedding if model not available
            return [0.1] * 384  # MiniLM-L6-v2 has 384 dimensions
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.1] * 384
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            return [[0.1] * 384 for _ in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return [[0.1] * 384 for _ in texts]
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

# Singleton instance
embedding_service = EmbeddingService()
