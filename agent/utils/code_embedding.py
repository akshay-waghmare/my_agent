"""
Code embedding and retrieval utilities for the AutoGen Coding Agent.
This module provides functions for embedding code and retrieving relevant snippets.
Uses only local embeddings to avoid external API dependencies.
"""

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pathlib import Path
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_embeddings(config):
    """
    Create embeddings based on configuration (Local only)
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Local embeddings instance
    """
    try:
        from .embedding_local import LocalEmbeddings
        rag_config = config.get("rag", {})
        model_name = rag_config.get("local_embeddings_model", "all-MiniLM-L6-v2")
        logger.info(f"Using local embeddings with model: {model_name}")
        return LocalEmbeddings(model_name)
    except ImportError as e:
        logger.error(f"Local embeddings not available ({e}). Please install: pip install sentence-transformers")
        # Return a simple fallback embeddings class
        return SimpleLocalEmbeddings()

class SimpleLocalEmbeddings:
    """Simple fallback embeddings when sentence-transformers is not available"""
    
    def embed_documents(self, texts):
        """Simple hash-based embedding fallback"""
        import hashlib
        embeddings = []
        for text in texts:
            # Create a simple numeric representation
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            # Convert to a simple vector (just for demonstration)
            embedding = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(32, len(hash_hex)), 2)]
            # Pad to consistent length
            embedding = (embedding + [0.0] * 16)[:16]
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Simple hash-based query embedding"""
        return self.embed_documents([text])[0]

def embed_codebase(config, code_dir="project-code", tasks_dir="agent", tasks_file="tasks.md", 
                file_extensions=None):
    """
    Load and embed the codebase
    
    Args:
        config (dict): Configuration dictionary
        code_dir (str): Directory containing the code to embed
        tasks_dir (str): Directory containing the tasks file
        tasks_file (str): Filename of the tasks file
        file_extensions (list): List of file extensions to include
        
    Returns:
        FAISS: Vector store with embedded documents
    """
    print(f"Loading and embedding codebase from {code_dir}...")
    
    # Ensure paths are absolute
    if not os.path.isabs(code_dir):
        code_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), code_dir)
    
    documents = []
      # Set default file extensions if none provided
    if file_extensions is None:
        file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.md', '.txt', '.html', '.css']
    
    # Load code files manually to avoid unstructured dependency
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Create a document-like object
                        from langchain.schema import Document
                        doc = Document(
                            page_content=content,
                            metadata={"source": file_path}
                        )
                        documents.append(doc)
                        print(f"Loaded file: {file_path}")
                except Exception as e:
                    print(f"Error loading file {file_path}: {e}")
                    continue    # Also load tasks file
    # Try various paths for tasks file
    possible_task_paths = [
        tasks_file,  # Use direct path if absolute
        os.path.join(os.path.dirname(os.path.dirname(__file__)), tasks_file),  # agent/utils/../tasks_file
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), tasks_file), # project_root/tasks_file
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agent", tasks_file.split('/')[-1]), # project_root/agent/tasks_file
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agent", tasks_file) # project_root/agent/tasks_file (full path)
    ]
    
    tasks_loaded = False
    for tasks_path in possible_task_paths:
        if os.path.exists(tasks_path):
            try:
                with open(tasks_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    from langchain.schema import Document
                    doc = Document(
                        page_content=content,
                        metadata={"source": tasks_path}
                    )
                    documents.append(doc)
                    print(f"Loaded tasks file: {tasks_path}")
                    tasks_loaded = True
                    break
            except Exception as e:
                print(f"Error loading tasks file {tasks_path}: {e}")
    
    if not tasks_loaded:
        print(f"Warning: Could not find tasks file in any of these locations:")
        for path in possible_task_paths:
            print(f"  - {path}")
    
    if not documents:
        print("Warning: No documents loaded!")
        return None
      # Configure the text splitter based on config
    chunk_size = config.get("rag", {}).get("chunk_size", 1000)
    chunk_overlap = config.get("rag", {}).get("chunk_overlap", 100)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_splitter.split_documents(documents)
    
    print(f"Loaded {len(documents)} documents, split into {len(texts)} chunks")

    # Create embeddings based on config
    embeddings = create_embeddings(config)
    db = FAISS.from_documents(texts, embeddings)
    return db

def query_codebase(index, query, config):
    """
    Search the codebase for relevant code snippets
    
    Args:
        index (FAISS): Vector store with embedded documents
        query (str): Query string
        config (dict): Configuration dictionary
        
    Returns:
        str: Concatenated relevant code snippets
    """
    # Handle the case where no documents were loaded
    if index is None:
        print("Warning: No vector index available. Creating empty context.")
        return "No code context available. Please ensure the project directory contains files."
    k = config.get("rag", {}).get("similarity_top_k", 3)
    results = index.similarity_search(query, k=k)
    
    # Return formatted results with source information
    formatted_results = []
    for doc in results:
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content
        formatted_results.append(f"Source: {source}\n\n{content}")
    
    return "\n\n" + "-"*50 + "\n\n".join(formatted_results)
