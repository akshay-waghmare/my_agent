#!/usr/bin/env python
"""
Generic Project AutoGen Coding Agent Runner

This script allows you to run the coding agent on different project types.
It provides command-line arguments to customize the agent's behavior.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """
    Parse arguments and run the agent
    """
    parser = argparse.ArgumentParser(description="Run the AutoGen Coding Agent on any project")
    
    parser.add_argument("--project-dir", 
                        help="Directory containing the project code", 
                        default="project-code")
    
    parser.add_argument("--tasks-file", 
                        help="Path to tasks file (absolute or relative to agent directory)", 
                        default="tasks.md")
    
    parser.add_argument("--query", 
                        help="Custom query for code context retrieval", 
                        default="")
    
    parser.add_argument("--verbose", 
                        help="Enable verbose output", 
                        action="store_true")
    
    parser.add_argument("--project-type", 
                        help="Project type (web, python, javascript, game, etc.)", 
                        default="generic")
    
    parser.add_argument("--mcp-config", 
                        help="Path to MCP configuration file (.mcp.yaml)", 
                        default=".mcp.yaml")
    
    parser.add_argument("--multi-agent", 
                        help="Use the multi-agent system with specialized agents", 
                        action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Starting agent for {args.project_type} project in {args.project_dir}")
        print(f"Using tasks from: {args.tasks_file}")
        if args.multi_agent:
            print(f"Using multi-agent system with MCP config: {args.mcp_config}")
    
    # Import the agent module directly to avoid circular imports
    from agent.code_agent import main as agent_main
    
    # Set command-line args as environment variables to pass to agent_main
    os.environ["AGENT_PROJECT_DIR"] = args.project_dir
    os.environ["AGENT_TASKS_FILE"] = args.tasks_file
    os.environ["AGENT_QUERY"] = args.query
    os.environ["AGENT_PROJECT_TYPE"] = args.project_type
    os.environ["AGENT_MCP_CONFIG"] = args.mcp_config
    os.environ["AGENT_USE_MULTI"] = str(args.multi_agent)
    os.environ["AGENT_VERBOSE"] = str(args.verbose)
    
    # Run the agent
    agent_main()

if __name__ == "__main__":
    main()
