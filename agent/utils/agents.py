"""
Agent utilities for the AutoGen Coding Agent.
This module provides functions for creating and managing agents.
"""

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from .file_ops import read_file, write_file, apply_code_diff, create_file

def create_agents(config, function_map=None):
    """
    Create the AutoGen agents
    
    Args:
        config (dict): Configuration dictionary
        function_map (dict, optional): Dictionary mapping function names to functions
        
    Returns:
        tuple: (assistant_agent, user_agent)
    """
    # Configure the agents
    llm_config = {
        "model": config.get("llm", {}).get("model", "gpt-4"),
        "temperature": config.get("llm", {}).get("temperature", 0.2),
        "max_tokens": config.get("llm", {}).get("max_tokens", 2000),
    }
    
    # Create the assistant agent
    assistant = AssistantAgent(
        name="Coder",
        llm_config=llm_config,        system_message="""You are an expert coding assistant that can create, read, and modify files.

Your capabilities:
1. CREATE FILES: Call create_file(path, content) to create new files
2. READ FILES: Call file_reader(path) to read existing files  
3. MODIFY FILES: Call apply_diff(path, diff) to apply changes to existing files

When creating HTML files, use the .html extension and place them in the project-code directory.
When creating CSS files, use the .css extension.
When creating JavaScript files, use the .js extension.

IMPORTANT: Use function calls, not code blocks. Do not write Python code blocks.

Example:
Instead of: ```python\nfile_writer("path", "content")\n```
Do this: Call the function directly as instructed by the user.

Be proactive - when asked to create files, actually create them using function calls."""
    )
    
    # Default function map if none provided
    if function_map is None:
        function_map = {}
      # Always include core file operations
    core_functions = {
        "file_reader": read_file,
        "file_writer": write_file,
        "create_file": create_file,
        "apply_diff": apply_code_diff
    }
    
    # Merge with provided function map
    final_function_map = {**core_functions, **function_map}
    
    # Load extensions if enabled
    try:
        from ..extensions import load_extensions
        extension_functions = load_extensions(config)
        final_function_map.update(extension_functions)
    except ImportError:
        # Extensions not available
        pass    # Create the user proxy agent
    user = UserProxyAgent(
        name="You",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        function_map=final_function_map,
        code_execution_config=False  # Disable code execution completely
    )
    
    return (assistant, user)

def run_agent_conversation(user_agent, assistant_agent, context, tasks):
    """
    Run the conversation between the user and assistant agents
    
    Args:
        user_agent (UserProxyAgent): User proxy agent
        assistant_agent (AssistantAgent): Assistant agent
        context (str): Context information (code snippets, etc.)
        tasks (str): Tasks to complete
        
    Returns:
        None
    """    # Start the conversation
    user_agent.initiate_chat(
        assistant_agent,        message=f"""Here is some code context:\n\n{context}
        
Tasks to complete:
{tasks}

IMPORTANT: You have file creation and modification capabilities. Use function calls, not code blocks!

Available functions (call them directly):
- create_file(path, content): CREATE new files (preferred for new files)
- file_writer(path, content): WRITE/overwrite files
- file_reader(path): READ existing files
- apply_diff(path, diff): MODIFY existing files

For Task 1: Call create_file("project-code/index.html", "html_content") to create the HTML file.
For Task 2: Call file_reader() to read the file, then apply_diff() to add styling.

Start with Task 1 and CREATE the HTML file by calling the create_file function.

Do NOT write Python code blocks. Use function calls directly.
"""
    )
