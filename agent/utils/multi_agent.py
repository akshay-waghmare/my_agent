"""
Multi-Agent Orchestration for the AutoGen Coding Agent.
This module provides functions for managing and coordinating multiple agents.
"""

import autogen
from autogen import GroupChat, GroupChatManager
from typing import Dict, List, Any
from pathlib import Path
import os
import yaml
import json

from .specialized_agents import (
    get_planner_agent, 
    get_coder_agent,
    get_reviewer_agent,
    get_test_agent,
    get_devops_agent,
    get_documentation_agent
)
from .file_ops import read_file, write_file, apply_code_diff, create_file, load_tasks

def load_mcp_config(config_path=None):
    """
    Load MCP (Model Context Protocol) configuration
    
    Args:
        config_path (str, optional): Path to .mcp.yaml file
        
    Returns:
        dict: MCP configuration
    """
    # Default MCP config
    default_config = {
        "version": "1.0",
        "agents": ["planner", "coder", "reviewer"],
        "goals": [
            "Implement all required functionality",
            "Ensure code is well-documented",
            "Follow best practices"
        ],
        "constraints": [
            "Do not modify any file outside the project directory",
            "Do not use external dependencies without explicit approval"
        ],
        "workflow": "sequential"  # or "collaborative"
    }
    
    if config_path is None:
        # Try to find .mcp.yaml in common locations
        possible_paths = [
            Path(".mcp.yaml"),
            Path(".mcp/config.yaml"),
            Path("agent/.mcp.yaml"),
        ]
        
        for p in possible_paths:
            if p.exists():
                config_path = p
                break
    
    # If config file exists, load it
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                mcp_config = yaml.safe_load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in mcp_config:
                        mcp_config[key] = default_config[key]
                return mcp_config
        except Exception as e:
            print(f"Error loading MCP config: {e}")
            return default_config
    else:
        return default_config

def create_agent_group(config, function_map=None, project_type="generic", project_dir="project-code"):
    """
    Create a group of agents based on configuration
    
    Args:
        config (dict): Configuration dictionary
        function_map (dict, optional): Dictionary of functions for agents to use
        project_type (str): Type of project
        project_dir (str): Directory containing the project
        
    Returns:
        tuple: (group_chat, manager, agent_dict)
    """
    # Load MCP configuration
    mcp_config = load_mcp_config()
    
    # Create agents based on MCP config
    agents = []
    agent_dict = {}
    
    # Default function map
    if function_map is None:
        function_map = {}
    
    # Core file operations
    core_functions = {
        "file_reader": read_file,
        "file_writer": write_file,
        "create_file": create_file,
        "apply_diff": apply_code_diff
    }
    
    # Merge function maps
    final_function_map = {**core_functions, **function_map}
    
    # Load extensions if enabled
    try:
        from ..extensions import load_extensions
        extension_functions = load_extensions(config)
        final_function_map.update(extension_functions)
    except ImportError:
        # Extensions not available
        pass
    
    # Create UserProxy for function execution
    user_proxy = autogen.UserProxyAgent(
        name="UserProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        function_map=final_function_map,
        code_execution_config=False  # Disable code execution
    )
    
    # Add user proxy to agents list
    agents.append(user_proxy)
    agent_dict["user_proxy"] = user_proxy
    
    # Create the specified agents based on MCP config
    agent_creators = {
        "planner": get_planner_agent,
        "coder": get_coder_agent,
        "reviewer": get_reviewer_agent,
        "test": get_test_agent,
        "devops": get_devops_agent,
        "documentation": get_documentation_agent
    }
    
    # Add requested agents
    for agent_name in mcp_config["agents"]:
        if agent_name.lower() in agent_creators:
            if agent_name.lower() == "coder":
                # Pass project_type to coder agent
                agent = agent_creators[agent_name.lower()](config, project_type)
            else:
                agent = agent_creators[agent_name.lower()](config)
            
            agents.append(agent)
            agent_dict[agent_name.lower()] = agent
    
    # Create the group chat
    group_chat = GroupChat(
        agents=agents,
        messages=[],
        max_round=config.get("agent", {}).get("max_iterations", 15)
    )
    
    # Create the group chat manager
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config={
            "model": config.get("llm", {}).get("model", "gpt-4"),
            "temperature": config.get("llm", {}).get("temperature", 0.2),
            "max_tokens": config.get("llm", {}).get("max_tokens", 2000),
        }
    )
    
    return group_chat, manager, agent_dict

def run_multi_agent_workflow(config, context, tasks, project_dir="project-code", project_type="generic"):
    """
    Run a multi-agent workflow based on tasks and configuration
    
    Args:
        config (dict): Configuration dictionary
        context (str): Context information (code snippets, etc.)
        tasks (str): Tasks to complete
        project_dir (str): Target project directory
        project_type (str): Type of project
    
    Returns:
        None
    """
    # Create function map for file operations
    function_map = {
        "create_file": create_file,
        "write_file": write_file,
        "read_file": read_file,
        "apply_diff": apply_code_diff
    }
    
    # Create the agent group
    group_chat, manager, agent_dict = create_agent_group(
        config, 
        function_map=function_map,
        project_type=project_type,
        project_dir=project_dir
    )
    
    # Load MCP configuration
    mcp_config = load_mcp_config()
    
    # Start the conversation
    user_proxy = agent_dict["user_proxy"]
    
    # Generate initial message
    initial_message = f"""# Project Development Task

## Context
{context}

## Tasks to Complete
{tasks}

## Goals
{json.dumps(mcp_config.get('goals', []), indent=2)}

## Constraints
{json.dumps(mcp_config.get('constraints', []), indent=2)}

## Project Information
- Project Type: {project_type}
- Project Directory: {project_dir}

## Available Functions
- create_file(path, content): CREATE new files
- file_writer(path, content): WRITE/overwrite files
- file_reader(path): READ existing files
- apply_diff(path, diff): MODIFY existing files

## Instructions
Please work through the tasks one by one, following the goals and respecting the constraints. 
Each agent should focus on their specialized area.
"""
    
    # Start the conversation
    user_proxy.initiate_chat(
        manager,
        message=initial_message
    )
