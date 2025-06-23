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

class CodeEmbeddings(LocalEmbeddings):
    """
    Specialized embeddings for code files.
    Uses a model optimized for code understanding.
    """
    
    def __init__(self, cache_folder: Optional[str] = None):
        # Use a model better suited for code
        super().__init__(
            model_name="microsoft/codebert-base", 
            cache_folder=cache_folder
        )

def get_available_models():
    """
    Get list of recommended models for different use cases
    
    Returns:
        Dict of model categories and their recommended models
    """
    return {
        "general": [
            "all-MiniLM-L6-v2",  # Fast and good quality
            "all-mpnet-base-v2",  # Higher quality, slower
            "all-MiniLM-L12-v2"   # Balance of speed and quality
        ],
        "code": [
            "microsoft/codebert-base",
            "microsoft/graphcodebert-base",
            "huggingface/CodeBERTa-small-v1"
        ],
        "multilingual": [
            "paraphrase-multilingual-MiniLM-L12-v2",
            "distiluse-base-multilingual-cased"
        ]
    }

def create_embedding_instance(provider: str = "openai", model_name: str = None, **kwargs):
    """
    Factory function to create embedding instances
    
    Args:
        provider: 'openai' or 'local'
        model_name: Model name (provider-specific)
        **kwargs: Additional arguments
        
    Returns:
        Embeddings instance
    """
    if provider.lower() == "local":
        if model_name is None:
            model_name = "all-MiniLM-L6-v2"
        return LocalEmbeddings(model_name=model_name, **kwargs)
    
    elif provider.lower() == "code":
        return CodeEmbeddings(**kwargs)
    elif provider.lower() == "openai":
        logger.error("OpenAI embeddings disabled to avoid API calls. Use local embeddings instead.")
        raise ValueError("OpenAI embeddings are disabled. Please use 'local' or 'code' provider instead.")
    
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")

# Utility functions for testing and benchmarking
def test_embedding_speed(texts: List[str], embedding_instance):
    """
    Test embedding speed for a given instance
    
    Args:
        texts: Sample texts to embed
        embedding_instance: Embeddings instance to test
        
    Returns:
        Dict with timing information
    """
    import time
    
    start_time = time.time()
    embeddings = embedding_instance.embed_documents(texts)
    end_time = time.time()
    
    return {
        "total_time": end_time - start_time,
        "texts_count": len(texts),
        "avg_time_per_text": (end_time - start_time) / len(texts),
        "embedding_dimension": len(embeddings[0]) if embeddings else 0
    }

def compare_embedding_providers(sample_texts: List[str]):
    """
    Compare different embedding providers
    
    Args:
        sample_texts: Texts to use for comparison
        
    Returns:
        Dict with comparison results
    """
    results = {}
    
    # Test local embeddings
    try:
        local_emb = create_embedding_instance("local")
        results["local"] = test_embedding_speed(sample_texts, local_emb)
        results["local"]["status"] = "success"
    except Exception as e:
        results["local"] = {"status": "error", "error": str(e)}
    
    # Test OpenAI embeddings (if available)
    try:
        openai_emb = create_embedding_instance("openai")
        results["openai"] = test_embedding_speed(sample_texts, openai_emb)
        results["openai"]["status"] = "success"
    except Exception as e:
        results["openai"] = {"status": "error", "error": str(e)}
    
    return results
