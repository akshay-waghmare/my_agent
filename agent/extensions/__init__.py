"""
Extensions package for the AutoGen Coding Agent.

This package contains extension modules that add additional functionality
to the core agent. Extensions can be easily enabled/disabled through configuration.
"""

from .git_integration import GIT_FUNCTION_MAP

# Registry of available extensions
AVAILABLE_EXTENSIONS = {
    "git": {
        "name": "Git Integration",
        "description": "Provides Git version control functionality",
        "function_map": GIT_FUNCTION_MAP,
        "config_key": "git_integration"
    }
}

def load_extensions(config):
    """
    Load enabled extensions based on configuration
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Combined function map from all enabled extensions
    """
    function_map = {}
    
    extensions_config = config.get("extensions", {})
    
    for ext_id, ext_info in AVAILABLE_EXTENSIONS.items():
        config_key = ext_info["config_key"]
        
        if extensions_config.get(config_key, False):
            print(f"Loading extension: {ext_info['name']}")
            function_map.update(ext_info["function_map"])
        else:
            print(f"Extension disabled: {ext_info['name']}")
    
    return function_map

def get_available_extensions():
    """
    Get information about available extensions
    
    Returns:
        dict: Dictionary of available extensions with their info
    """
    return AVAILABLE_EXTENSIONS.copy()
