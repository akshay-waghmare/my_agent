"""
AutoGen Coding Agent - Main Entry Point

This is the main module for the AutoGen Coding Agent that combines
LangChain RAG capabilities with AutoGen multi-agent conversation.
It supports multiple specialized agents and configurable project types.
"""

import argparse
from dotenv import load_dotenv
from pathlib import Path
import os
import yaml

# Import our modular utilities
from agent.utils import (
    load_config,
    embed_codebase,
    query_codebase,
    load_tasks,
    create_agents,
    run_agent_conversation,
    # New multi-agent components
    create_agent_group,
    run_multi_agent_workflow,
    load_mcp_config
)

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the AutoGen Coding Agent
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AutoGen Coding Agent")
    parser.add_argument("--project-dir", help="Target project directory to analyze", 
                       default=os.environ.get("AGENT_PROJECT_DIR", "project-code"))
    parser.add_argument("--tasks-file", help="Path to tasks file", 
                       default=os.environ.get("AGENT_TASKS_FILE", "tasks.md"))
    parser.add_argument("--query", help="Search query for code context", 
                       default=os.environ.get("AGENT_QUERY", ""))
    parser.add_argument("--project-type", help="Type of project (web, python, javascript, java, game, etc.)", 
                       default=os.environ.get("AGENT_PROJECT_TYPE", "generic"))
    parser.add_argument("--mcp-config", help="Path to MCP configuration file", 
                       default=os.environ.get("AGENT_MCP_CONFIG", ".mcp.yaml"))
    parser.add_argument("--multi-agent", help="Use the multi-agent system", 
                       action="store_true", default=os.environ.get("AGENT_USE_MULTI", "false").lower() == "true")
    parser.add_argument("--verbose", help="Enable verbose output", 
                       action="store_true", default=os.environ.get("AGENT_VERBOSE", "true").lower() == "true")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override verbose setting if specified in args
    if args.verbose:
        config["agent"] = config.get("agent", {})
        config["agent"]["verbose"] = True
    
    if config.get("agent", {}).get("verbose", True):
        print("Starting AutoGen Coding Agent...")
        print(f"Using model: {config.get('llm', {}).get('model', 'gpt-4')}")
        print(f"Project directory: {args.project_dir}")
        print(f"Tasks file: {args.tasks_file}")
        print(f"Project type: {args.project_type}")
        if args.multi_agent:
            print("Using multi-agent system")
    
    # Try to load MCP config to enhance project_type and other settings
    try:
        mcp_config = load_mcp_config(args.mcp_config)
        # Update project type if specified in MCP config
        if "metadata" in mcp_config and "type" in mcp_config["metadata"]:
            project_type_from_mcp = mcp_config["metadata"]["type"].lower()
            if project_type_from_mcp and project_type_from_mcp != "generic":
                args.project_type = project_type_from_mcp
                if config.get("agent", {}).get("verbose", True):
                    print(f"Using project type from MCP config: {args.project_type}")
    except Exception as e:
        if config.get("agent", {}).get("verbose", True):
            print(f"Could not load MCP config: {e}")
    
    # Define file extensions for different project types
    file_extensions = {
        "web": [".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".json"],
        "python": [".py", ".ipynb", ".pyx", ".pyi", ".pyd", ".pyc"],
        "javascript": [".js", ".jsx", ".ts", ".tsx", ".json", ".mjs", ".cjs"],
        "java": [".java", ".class", ".jar", ".properties", ".xml"],
        "game": [".js", ".html", ".css", ".unity", ".cs", ".ts", ".cpp", ".h", ".py"],
        "generic": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".md", ".txt", ".html", ".css", ".json"]
    }
    
    # Use project type to customize behavior
    project_type = args.project_type.lower()
    extensions = file_extensions.get(project_type, file_extensions["generic"])
      
    # Create project directory if it doesn't exist
    if not os.path.exists(args.project_dir):
        os.makedirs(args.project_dir, exist_ok=True)
        if config.get("agent", {}).get("verbose", True):
            print(f"Created project directory: {args.project_dir}")
    
    # Embed the codebase
    db = embed_codebase(config, code_dir=args.project_dir, tasks_file=args.tasks_file, 
                       file_extensions=extensions)
    
    # Load tasks
    tasks = load_tasks(args.tasks_file)
    if config.get("agent", {}).get("verbose", True):
        print("Loaded tasks:")
        print(tasks)
    
    # Determine the search query based on tasks if none provided
    search_query = args.query
    if not search_query:
        # Extract a basic query from the tasks content
        search_query = tasks[:100]  # Use first 100 chars of tasks as default query
        if config.get("agent", {}).get("verbose", True):
            print(f"Using auto-generated query: {search_query}")
    
    # Query for relevant code based on tasks
    code_context = query_codebase(db, search_query, config)
    
    # Decide whether to use multi-agent or simple agent system
    if args.multi_agent:
        if config.get("agent", {}).get("verbose", True):
            print("Running multi-agent workflow...")
        
        # Run the multi-agent workflow
        run_multi_agent_workflow(
            config,
            code_context,
            tasks,
            project_dir=args.project_dir,
            project_type=project_type
        )
    else:
        if config.get("agent", {}).get("verbose", True):
            print("Running simple agent workflow...")
        
        # Create agents
        assistant, user = create_agents(config, project_type=project_type)
        
        # Run the conversation
        run_agent_conversation(user, assistant, code_context, tasks, project_dir=args.project_dir)

if __name__ == "__main__":
    main()
