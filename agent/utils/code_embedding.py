"""
Code embedding and retrieval utilities for the AutoGen Coding Agent.
This module provides functions for embedding code and retrieving relevant snippets.
"""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pathlib import Path
import os

def embed_codebase(config, code_dir="project-code", tasks_dir="agent", tasks_file="tasks.md"):
    """
    Load and embed the codebase
    
    Args:
        config (dict): Configuration dictionary
        code_dir (str): Directory containing the code to embed
        tasks_dir (str): Directory containing the tasks file
        tasks_file (str): Filename of the tasks file
        
    Returns:
        FAISS: Vector store with embedded documents
    """
    print("Loading and embedding codebase...")
    
    # Ensure paths are absolute
    if not os.path.isabs(code_dir):
        code_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), code_dir)
    
    documents = []
    
    # Load code files manually to avoid unstructured dependency
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.md', '.txt')):
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
                    continue
    
    # Also load tasks file
    tasks_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), tasks_file)
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
        except Exception as e:
            print(f"Error loading tasks file {tasks_path}: {e}")
    
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

    embeddings = OpenAIEmbeddings()
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
    k = config.get("rag", {}).get("similarity_top_k", 3)
    results = index.similarity_search(query, k=k)
    
    # Return formatted results with source information
    formatted_results = []
    for doc in results:
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content
        formatted_results.append(f"Source: {source}\n\n{content}")
    
    return "\n\n" + "-"*50 + "\n\n".join(formatted_results)
