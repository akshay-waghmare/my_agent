"""
AutoGen Coding Agent with MCP-Style Task Execution

This script implements an MCP-like approach for task execution that bypasses
the function calling issues in AutoGen and directly executes tasks.
"""

from dotenv import load_dotenv
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from agent.utils.config import load_config
from agent.utils.file_ops import read_file, write_file, create_file, apply_code_diff
from agent.mcp_loader_clean import MCPLoader

# Load environment variables
load_dotenv()

def main():
    """
    Main function that uses MCP-style task execution
    """
    print("🚀 Starting AutoGen Coding Agent (MCP-Style)")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
      # Initialize MCP loader
    mcp = MCPLoader(tasks_file="agent/tasks.md", config=config)
    
    # Register available tools
    mcp.register_tool("create_file", create_file, "Create a new file")
    mcp.register_tool("write_file", write_file, "Write content to a file")
    mcp.register_tool("read_file", read_file, "Read content from a file")
    mcp.register_tool("apply_diff", apply_code_diff, "Apply a diff to a file")
    
    print("🔧 Registered tools:", list(mcp.tools.keys()))
    
    # Load and parse tasks
    tasks = mcp.load_tasks()
    print(f"📋 Loaded {len(tasks)} tasks")
    
    # Execute all tasks
    results = mcp.run_all_tasks()
    
    # Print summary
    summary = mcp.get_summary(results)
    print(summary)
    
    # Show created files
    print("📁 Files created:")
    if os.path.exists("project-code"):
        for file in os.listdir("project-code"):
            file_path = os.path.join("project-code", file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   • {file} ({size} bytes)")
    
    print("\n🎉 Task execution completed!")
    
    # Offer to view the created HTML file
    if os.path.exists("project-code/index.html"):
        print("\n💡 You can view the created HTML file by opening: project-code/index.html")
        
        # Read and show a preview
        content = read_file("project-code/index.html")
        if content and len(content) < 1000:
            print("\n📄 HTML Preview:")
            print("-" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 30)

if __name__ == "__main__":
    main()
