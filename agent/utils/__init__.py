"""
Utility modules for the AutoGen Coding Agent.
"""

from .config import load_config
from .file_ops import read_file, write_file, apply_code_diff, load_tasks, create_file
from .enhanced_file_ops import (
    create_file_with_checks,
    read_file_with_context,
    detect_file_type,
    find_files_by_pattern,
    analyze_project_structure
)
from .code_embedding import embed_codebase, query_codebase
from .local_embeddings import LocalEmbeddings, create_local_embeddings, test_local_embeddings
from .agents import create_agents, run_agent_conversation
from .llm_client import create_llm_client, LLMClient
from .enhanced_llm import create_enhanced_llm_client, EnhancedLLMClient
from .specialized_agents import (
    get_planner_agent, 
    get_coder_agent,
    get_reviewer_agent,
    get_test_agent,
    get_devops_agent,
    get_documentation_agent
)
from .multi_agent import (
    create_agent_group,
    run_multi_agent_workflow,
    load_mcp_config
)

# Export all the functions
__all__ = [
    # Configuration
    'load_config',
    
    # File operations
    'read_file',
    'write_file',
    'apply_code_diff',
    'load_tasks',
    'create_file',
    
    # Enhanced file operations
    'create_file_with_checks',
    'read_file_with_context',
    'detect_file_type',
    'find_files_by_pattern',
    'analyze_project_structure',
      # Code embedding
    'embed_codebase',
    'query_codebase',
    
    # Local embeddings
    'LocalEmbeddings',
    'create_local_embeddings', 
    'test_local_embeddings',
    
    # Agent management
    'create_agents',
    'run_agent_conversation',
    
    # LLM clients
    'create_llm_client',
    'LLMClient',
    'create_enhanced_llm_client',
    'EnhancedLLMClient',
    
    # Specialized agents
    'get_planner_agent',
    'get_coder_agent',
    'get_reviewer_agent',
    'get_test_agent',
    'get_devops_agent',
    'get_documentation_agent',
    
    # Multi-agent system
    'create_agent_group',
    'run_multi_agent_workflow',
    'load_mcp_config'
]
