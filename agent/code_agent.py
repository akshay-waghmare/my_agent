"""
AutoGen Coding Agent - Main Entry Point

This is the main module for the AutoGen Coding Agent that combines
LangChain RAG capabilities with AutoGen multi-agent conversation.
"""

from dotenv import load_dotenv
from pathlib import Path

# Import our modular utilities
from utils import (
    load_config,
    embed_codebase,
    query_codebase,
    load_tasks,
    create_agents,
    run_agent_conversation
)

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the AutoGen Coding Agent
    """
    # Load configuration
    config = load_config()
    
    if config.get("agent", {}).get("verbose", True):
        print("Starting AutoGen Coding Agent...")
        print(f"Using model: {config.get('llm', {}).get('model', 'gpt-4')}")
    
    # Embed the codebase
    db = embed_codebase(config)
    
    # Load tasks
    tasks = load_tasks()
    if config.get("agent", {}).get("verbose", True):
        print("Loaded tasks:")
        print(tasks)
    
    # Query for relevant code based on tasks
    code_context = query_codebase(db, "bubble popping logic and color logic", config)
    
    # Create agents
    assistant, user = create_agents(config)
      # Run the conversation
    run_agent_conversation(user, assistant, code_context, tasks)

if __name__ == "__main__":
    main()
