"""
Test script to verify the modular structure of the AutoGen Coding Agent
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all utility modules can be imported"""
    try:
        print("Testing module imports...")
        
        # Test individual module imports
        from agent.utils.config import load_config
        print("✓ Config module imported successfully")
        
        from agent.utils.file_ops import read_file, write_file, load_tasks
        print("✓ File operations module imported successfully")
        
        from agent.utils.code_embedding import embed_codebase, query_codebase
        print("✓ Code embedding module imported successfully")
        
        from agent.utils.agents import create_agents, run_agent_conversation
        print("✓ Agents module imported successfully")
        
        # Test the main utility package import
        from agent.utils import load_config as util_load_config
        print("✓ Utils package import working")
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    try:
        print("\nTesting configuration loading...")
        from agent.utils.config import load_config
        
        config = load_config()
        
        # Check if required sections exist
        required_sections = ['llm', 'rag', 'agent']
        for section in required_sections:
            if section not in config:
                print(f"✗ Missing config section: {section}")
                return False
        
        print(f"✓ Configuration loaded with sections: {list(config.keys())}")
        return True
        
    except Exception as e:
        print(f"✗ Config loading error: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    try:
        print("\nTesting file operations...")
        from agent.utils.file_ops import read_file, write_file, load_tasks
        
        # Test reading an existing file
        content = read_file("README.md")
        if content and not content.startswith("Error") and len(content) > 100:
            print("✓ File reading working")
        else:
            print(f"✗ File reading failed or unexpected content: {content[:100] if content else 'None'}...")
            return False
        
        # Test task loading
        tasks = load_tasks()
        if "Task" in tasks or "task" in tasks.lower():
            print("✓ Task loading working")
        else:
            print("✗ Task loading failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ File operations error: {e}")
        return False

if __name__ == "__main__":
    print("AutoGen Coding Agent - Module Test")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_config_loading()
    success &= test_file_operations()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! The modular structure is working correctly.")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        sys.exit(1)
