"""
Test script to demonstrate the MCP Loader functionality
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from agent.mcp_loader import MCPLoader
from agent.utils.file_ops import create_file, write_file, read_file

def test_mcp_loader():
    """Test the MCP loader with the current tasks"""
    print("🚀 Testing MCP Loader...")
    
    # Initialize the loader
    loader = MCPLoader("agent/tasks.md")
    
    # Register tools
    loader.register_tool("create_file", create_file, "Create a new file")
    loader.register_tool("write_file", write_file, "Write content to a file")
    loader.register_tool("read_file", read_file, "Read content from a file")
    
    # Load tasks
    tasks = loader.load_tasks()
    print(f"\n📋 Loaded {len(tasks)} tasks:")
    for task in tasks:
        print(f"   Task {task['id']}: {task['name']} ({task['type']})")
    
    # Execute all tasks
    print("\n⚡ Executing tasks...")
    results = loader.run_all_tasks()
    
    # Show summary
    summary = loader.get_summary(results)
    print(summary)
    
    # Verify the files were created
    print("🔍 Verifying created files...")
    if os.path.exists('project-code/index.html'):
        print("✅ index.html created successfully!")
        
        # Show a preview of the content
        with open('project-code/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n📄 File preview (first 300 characters):")
        print("-" * 50)
        print(content[:300] + "..." if len(content) > 300 else content)
        print("-" * 50)
    else:
        print("❌ index.html was not created")

if __name__ == "__main__":
    test_mcp_loader()
