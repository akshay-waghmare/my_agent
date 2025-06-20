"""
MCP Loader Runner - Main entry point for the MCP-style task execution
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from agent.mcp_loader import MCPLoader
from agent.utils.file_ops import create_file, write_file, read_file

def main():
    """Main entry point for MCP loader"""
    print("🤖 AutoGen Coding Agent - MCP Loader")
    print("=====================================")
    
    # Initialize the loader
    loader = MCPLoader("agent/tasks.md")
    
    # Register available tools
    loader.register_tool("create_file", create_file, "Create a new file")
    loader.register_tool("write_file", write_file, "Write content to a file")
    loader.register_tool("read_file", read_file, "Read content from a file")
    
    print("🔧 Registered tools: create_file, write_file, read_file")
    
    # Load and execute tasks
    tasks = loader.load_tasks()
    
    if not tasks:
        print("❌ No tasks found. Please check your tasks.md file.")
        return
    
    print(f"\n📋 Found {len(tasks)} tasks to execute")
    
    # Execute all tasks
    results = loader.run_all_tasks()
    
    # Show summary
    summary = loader.get_summary(results)
    print(summary)
    
    # Show created files
    project_code_dir = "project-code"
    if os.path.exists(project_code_dir):
        files = [f for f in os.listdir(project_code_dir) if os.path.isfile(os.path.join(project_code_dir, f))]
        if files:
            print("📁 Files created:")
            for file in files:
                file_path = os.path.join(project_code_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   • {file} ({file_size} bytes)")
        
        print(f"\n🎉 Task execution completed!")
        print(f"💡 You can view the created HTML file by opening: {project_code_dir}/index.html")

if __name__ == "__main__":
    main()
