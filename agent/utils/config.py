"""
Configuration utilities for the AutoGen Coding Agent.
This module provides functions for loading and managing configuration.
"""

import yaml
from pathlib import Path
import os

def load_config(config_file=None):
    """
    Load configuration from a YAML file
    
    Args:
        config_file (str, optional): Path to the config file. If None, uses default location.
        
    Returns:
        dict: Configuration dictionary
    """
    # Default config
    default_config = {
        "llm": {
            "model": "gpt-4", 
            "temperature": 0.2,
            "max_tokens": 2000
        },
        "rag": {
            "chunk_size": 1000, 
            "chunk_overlap": 100, 
            "similarity_top_k": 3
        },
        "agent": {
            "max_iterations": 5, 
            "verbose": True
        },
        "extensions": {
            "git_integration": False,
            "file_writing": True
        }
    }
    
    # If no config file specified, use default location
    if config_file is None:
        config_file = Path(__file__).parent.parent / "config.yaml"
    else:
        config_file = Path(config_file)
    
    # If config file exists, load it and update default config
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                
            # Update default config with user config
            if user_config:
                # Merge nested dictionaries
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict) and isinstance(default_config[key], dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
            print("Using default configuration.")
    
    return default_config
