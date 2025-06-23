"""
Local embedding utilities using Sentence Transformers.
Provides an alternative to OpenAI embeddings for offline/local usage.
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional
from langchain.embeddings.base import Embeddings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbeddings(Embeddings):
    """
    Local embeddings using Sentence Transformers.
    Compatible with LangChain's Embeddings interface.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_folder: Optional[str] = None):
        """
        Initialize local embeddings
        
        Args:
            model_name: Sentence transformer model name
            cache_folder: Directory to cache models (optional)
        """
        self.model_name = model_name
        self.cache_folder = cache_folder or os.path.join(os.getcwd(), ".cache", "sentence-transformers")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Ensure cache directory exists
            os.makedirs(self.cache_folder, exist_ok=True)
            
            logger.info(f"Loading local embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name, 
                cache_folder=self.cache_folder
            )
            logger.info(f"✅ Local embedding model loaded successfully")
            
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install it with: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embeddings (as lists of floats)
        """
        if not self.model:
            self._load_model()
            
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Convert to list of lists for compatibility
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding as list of floats
        """
        if not self.model:
            self._load_model()
            
        try:
            # Generate embedding for single text
            embedding = self.model.encode([text], convert_to_numpy=True)
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

# Available local embedding models
LOCAL_EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2": {
        "description": "Fast and efficient model, 384 dimensions",
        "size": "80MB",
        "performance": "Good",
        "speed": "Fast"
    },
    "all-mpnet-base-v2": {
        "description": "High quality model, 768 dimensions",
        "size": "420MB", 
        "performance": "Excellent",
        "speed": "Medium"
    },
    "paraphrase-MiniLM-L6-v2": {
        "description": "Optimized for paraphrase detection",
        "size": "80MB",
        "performance": "Good",
        "speed": "Fast"
    },
    "multi-qa-MiniLM-L6-cos-v1": {
        "description": "Optimized for question-answering",
        "size": "80MB", 
        "performance": "Good for QA",
        "speed": "Fast"
    },
    "all-distilroberta-v1": {
        "description": "Balanced performance model",
        "size": "290MB",
        "performance": "Very Good",
        "speed": "Medium"
    }
}

def get_available_models() -> Dict[str, Dict[str, str]]:
    """Get information about available local embedding models"""
    return LOCAL_EMBEDDING_MODELS

def create_local_embeddings(model_name: str = "all-MiniLM-L6-v2", 
                           cache_folder: Optional[str] = None) -> LocalEmbeddings:
    """
    Factory function to create local embeddings
    
    Args:
        model_name: Name of the sentence transformer model
        cache_folder: Directory to cache models
        
    Returns:
        LocalEmbeddings instance
    """
    return LocalEmbeddings(model_name, cache_folder)

def test_local_embeddings(model_name: str = "all-MiniLM-L6-v2") -> bool:
    """
    Test local embeddings functionality
    
    Args:
        model_name: Model to test
        
    Returns:
        True if test passes, False otherwise
    """
    try:
        logger.info(f"Testing local embeddings with model: {model_name}")
        
        # Create embeddings instance
        embeddings = LocalEmbeddings(model_name)
        
        # Test documents
        test_docs = [
            "This is a test document about machine learning.",
            "Python is a programming language.",
            "Vector embeddings represent text as numerical vectors."
        ]
        
        # Test query
        test_query = "What is machine learning?"
        
        # Embed documents
        doc_embeddings = embeddings.embed_documents(test_docs)
        logger.info(f"✅ Successfully embedded {len(doc_embeddings)} documents")
        
        # Embed query
        query_embedding = embeddings.embed_query(test_query)
        logger.info(f"✅ Successfully embedded query, dimension: {len(query_embedding)}")
        
        # Verify embeddings have correct shape
        if len(doc_embeddings) != len(test_docs):
            logger.error("❌ Number of document embeddings doesn't match input")
            return False
            
        if not all(len(emb) == len(query_embedding) for emb in doc_embeddings):
            logger.error("❌ Embedding dimensions don't match")
            return False
            
        logger.info("✅ Local embeddings test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Local embeddings test failed: {e}")
        return False
