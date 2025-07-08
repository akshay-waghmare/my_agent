#!/usr/bin/env python3
"""
Test script to verify LLM-driven agent functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from agent.mcp_loader import MCPLoader
from agent.utils.file_ops import create_file, read_file, write_file

def test_llm_agent():
    """Test the LLM-driven agent with sample tasks"""
    print("🧪 Testing LLM-Driven Agent")
    print("=" * 50)
    
    # Initialize MCPLoader with LLM config
    config = {
        'llm': {
            'provider': 'lmstudio',
            'temperature': 0.3,
            'max_tokens': 2000
        }
    }
    
    loader = MCPLoader("test_tasks.md", config)
    
    # Register tools
    loader.register_tool("create_file", create_file, "Create a new file")
    loader.register_tool("write_file", write_file, "Write content to a file")
    loader.register_tool("read_file", read_file, "Read content from a file")
    
    print("🔧 Registered tools successfully")
    
    # Load tasks
    tasks = loader.load_tasks()
    print(f"📋 Loaded {len(tasks)} tasks")
    
    if not tasks:
        print("❌ No tasks found!")
        return False
    
    # Print loaded tasks
    for task in tasks:
        print(f"  - Task {task['id']}: {task['name']}")
        for step in task['steps']:
            print(f"    • {step}")
    
    print("\n🤖 Starting LLM-driven task execution...")
    
    # Execute tasks
    try:
        results = loader.run_all_tasks()
        
        # Print results
        print("\n📊 Execution Results:")
        print("=" * 30)
        
        for result in results:
            status = "✅" if result['overall_success'] else "❌"
            print(f"{status} Task {result['task_id']}: {result['task_name']}")
            print(f"   Steps executed: {result['steps_executed']}")
            
            for step_result in result['results']:
                step_status = "✅" if step_result['success'] else "❌"
                print(f"   {step_status} {step_result['step'][:50]}...")
        
        # Show summary
        summary = loader.get_summary(results)
        print("\n📝 Summary:")
        print(summary)
        
        # Check if files were created
        project_dir = Path("project-code")
        if project_dir.exists():
            files = list(project_dir.glob("*"))
            print(f"\n📁 Created {len(files)} files:")
            for file in files:
                print(f"   - {file.name} ({file.stat().st_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_agent()
    if success:
        print("\n🎉 LLM-driven agent test completed successfully!")
    else:
        print("\n💥 LLM-driven agent test failed!")
        sys.exit(1)
