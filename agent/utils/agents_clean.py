"""
Agent utilities for the AutoGen Coding Agent.
This module provides functions for creating and managing agents.
"""

import os
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from .file_ops import read_file, write_file, apply_code_diff, create_file
from .enhanced_file_ops import create_file_with_checks, read_file_with_context
from .enhanced_llm import create_enhanced_llm_client

def create_agents(config, function_map=None, project_type="generic", project_dir=None):
    """
    Create the AutoGen agents
    
    Args:
        config (dict): Configuration dictionary
        function_map (dict, optional): Dictionary mapping function names to functions
        project_type (str): Optional project type hint - LLM will adapt automatically
        project_dir (str, optional): Path to project directory
        
    Returns:
        tuple: (assistant_agent, user_agent)
    """
    # Create enhanced LLM client and get configuration
    llm_client = create_enhanced_llm_client(config)
    llm_config = llm_client.get_autogen_config()
    
    # Print provider information if verbose
    if config.get("agent", {}).get("verbose", True):
        provider_info = llm_client.get_provider_info()
        print(f"Using {provider_info['provider']} provider with model: {provider_info['model']}")
        if provider_info['api_base'] != "default":
            print(f"API Base: {provider_info['api_base']}")
    
    # Create the assistant agent with a smart, adaptive system message
    system_message = """You are an expert coding assistant that can create, read, and modify files.

Your capabilities:
1. CREATE FILES: Call create_file(path, content) to create new files
2. READ FILES: Call read_file(path) to read existing files  
3. MODIFY FILES: Call apply_code_diff(path, diff) to apply changes to existing files
4. ENHANCED CREATE: Call create_file_with_checks(path, content) for smart file creation with validation

CRITICAL: You MUST use function calls to perform file operations. Do NOT just describe what you would do.

Example of CORRECT behavior:
User: "Create an HTML file"
You: I'll create the HTML file now.
Then immediately call: create_file("index.html", "<!DOCTYPE html>...")

Example of INCORRECT behavior:
User: "Create an HTML file" 
You: "I can't create files, but here's what the content should be..."

IMPORTANT RULES:
- When asked to create/modify files, DO IT immediately using function calls
- Always call the functions, never just provide code examples
- Generate complete, functional content for each file
- Follow modern development best practices for whatever technology stack you detect
- Include comprehensive comments in your code
- Automatically detect the project type from context and adapt accordingly
- Use appropriate file extensions and project structure based on what you observe

ADAPTIVE BEHAVIOR:
- If you see package.json, assume it's a Node.js/JavaScript project
- If you see requirements.txt or .py files, assume it's a Python project
- If you see HTML/CSS files, assume it's a web project
- If you see game-related terms or assets, assume it's a game project
- Adapt your coding style and practices to match the detected technology stack

Be proactive - when asked to create files, actually create them using function calls immediately."""
    
    # Create the assistant agent
    assistant = AssistantAgent(
        name="Coder",
        llm_config=llm_config,
        system_message=system_message
    )
    
    # Default function map if none provided
    if function_map is None:
        function_map = {}
    
    # Always include core file operations
    core_functions = {
        "file_reader": read_file,
        "file_writer": write_file,
        "create_file": create_file,
        "apply_diff": apply_code_diff,
        "create_file_with_checks": create_file_with_checks,
        "read_file_with_context": read_file_with_context
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
        pass
    
    # Register functions with the assistant agent for LLM calls
    assistant.register_for_llm(description="Create a new file with content")(create_file)
    assistant.register_for_llm(description="Read content from a file")(read_file)
    assistant.register_for_llm(description="Write content to a file")(write_file)
    assistant.register_for_llm(description="Apply code diff to a file")(apply_code_diff)
    assistant.register_for_llm(description="Create file with validation checks")(create_file_with_checks)
    assistant.register_for_llm(description="Read file with additional context")(read_file_with_context)

    # Create the user proxy agent
    user = UserProxyAgent(
        name="You",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        function_map=final_function_map,
        code_execution_config=False  # Disable code execution completely
    )
    
    # Register functions for execution with UserProxy
    user.register_for_execution()(create_file)
    user.register_for_execution()(read_file) 
    user.register_for_execution()(write_file)
    user.register_for_execution()(apply_code_diff)
    user.register_for_execution()(create_file_with_checks)
    user.register_for_execution()(read_file_with_context)
    
    return (assistant, user)

def run_agent_conversation(user_agent, assistant_agent, context, tasks, project_dir="project-code"):
    """
    Run the conversation between the user and assistant agents
    
    Args:
        user_agent (UserProxyAgent): User proxy agent
        assistant_agent (AssistantAgent): Assistant agent
        context (str): Context information (code snippets, etc.)
        tasks (str): Tasks to complete
        project_dir (str): Target project directory
        
    Returns:
        None
    """
    # Start the conversation
    user_agent.initiate_chat(
        assistant_agent,
        message=f"""Here is some code context:

{context}
        
Tasks to complete:
{tasks}

IMPORTANT: You have file creation and modification capabilities. Use function calls, not code blocks!

Available functions (call them directly):
- create_file(path, content): CREATE new files (preferred for new files)
- file_writer(path, content): WRITE/overwrite files
- file_reader(path): READ existing files
- apply_diff(path, diff): MODIFY existing files
- create_file_with_checks(path, content): CREATE with validation
- read_file_with_context(path): READ with additional context

The target project directory is: {project_dir}

Please work through the tasks one by one and implement the requested functionality.

Do NOT write Python code blocks. Use function calls directly.
"""
    )
