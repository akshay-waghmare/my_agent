#!/usr/bin/env python3
"""
Quick test to verify local embeddings are working
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_local_embeddings():
    """Test local embeddings functionality"""
    print("🧪 Testing Local Embeddings")
    print("=" * 40)
    
    try:
        from agent.utils.code_embedding import create_embeddings, SimpleLocalEmbeddings
        
        # Test configuration
        config = {
            "rag": {
                "embeddings_provider": "local",
                "local_embeddings_model": "all-MiniLM-L6-v2"
            }
        }
        
        print("🔧 Creating embeddings instance...")
        embeddings = create_embeddings(config)
        
        if isinstance(embeddings, SimpleLocalEmbeddings):
            print("✅ Using SimpleLocalEmbeddings (fallback)")
        else:
            print("✅ Using LocalEmbeddings (sentence-transformers)")
        
        # Test embedding some text
        print("\n📝 Testing text embedding...")
        test_texts = [
            "def hello_world(): print('Hello, World!')",
            "function greet() { console.log('Hello!'); }",
            "print('This is a test')"
        ]
        
        embeddings_result = embeddings.embed_documents(test_texts)
        print(f"✅ Embedded {len(test_texts)} documents")
        print(f"   First embedding shape: {len(embeddings_result[0])} dimensions")
        
        # Test query embedding
        query = "python function"
        query_embedding = embeddings.embed_query(query)
        print(f"✅ Query embedding shape: {len(query_embedding)} dimensions")
        
        print("\n🎉 Local embeddings test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_local_embeddings()
    if not success:
        sys.exit(1)
