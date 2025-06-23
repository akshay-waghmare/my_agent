"""
Specialized Agents for the AutoGen Coding Agent.
This module defines various specialized agents for different development tasks.
"""

from autogen import AssistantAgent
from .file_ops import read_file, write_file, apply_code_diff, create_file, load_tasks
from .llm_client import create_llm_client
from typing import Dict, Any

def get_planner_agent(config: Dict[str, Any]):
    """
    Create a Planner Agent that breaks down tasks into subtasks
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        AssistantAgent: The planner agent
    """
    # Create LLM client and get configuration
    llm_client = create_llm_client(config)
    llm_config = llm_client.get_autogen_config()
    
    system_message = """You are a Project Planning Expert.

Your primary responsibility is to analyze project requirements and break them down into clear, manageable tasks.

When given a project specification or feature request:
1. Identify the main components/modules needed
2. Break down the work into clearly defined tasks
3. Establish dependencies between tasks
4. Estimate complexity for each task
5. Suggest a logical implementation order

Focus on architectural decisions, component interactions, and data flow.
Always consider scalability, maintainability, and best practices for the specific technology stack.

Output tasks in a structured format with clear acceptance criteria.
"""
    
    return AssistantAgent(
        name="Planner",
        llm_config=llm_config,
        system_message=system_message
    )

def get_coder_agent(config: Dict[str, Any], project_type: str = "generic"):
    """
    Create a Coder Agent that writes actual code
    
    Args:
        config (dict): Configuration dictionary
        project_type (str): Type of project
    
    Returns:
        AssistantAgent: The coder agent
    """
    # Create LLM client and get configuration
    llm_client = create_llm_client(config)
    llm_config = llm_client.get_autogen_config()
    
    def get_system_message(project_type="generic"):
        base_message = """You are an expert coding assistant that can create, read, and modify files.

Your capabilities:
1. CREATE FILES: create_file(path, content) - Creates new files
2. READ FILES: read_file(path) - Reads existing files  
3. WRITE FILES: write_file(path, content) - Writes/overwrites files
4. MODIFY FILES: apply_diff(path, diff) - Applies changes to existing files

IMPORTANT: Use proper function calls, not descriptive code blocks. 

CORRECT EXAMPLE:
To create a file, simply use: create_file("path/to/file.txt", "file content")

INCORRECT:
Call create_file("path", "content") or Call the function directly
```python
create_file("path", "content") 
```

Be proactive - when asked to create files, actually create them using function calls."""

        # Add project-specific instructions
        project_messages = {
            "web": """
You specialize in web development using HTML, CSS, JavaScript.
When creating HTML files, use the .html extension.
When creating CSS files, use the .css extension.
When creating JavaScript files, use the .js extension.
Follow web development best practices and ensure responsive design.""",
            
            "python": """
You specialize in Python development.
When creating Python files, use the .py extension.
Follow PEP 8 style guidelines and include appropriate docstrings.
Consider including tests for your code when appropriate.""",
            
            "javascript": """
You specialize in JavaScript/TypeScript development.
When creating JavaScript files, use the .js extension.
When creating TypeScript files, use the .ts extension.
Follow modern JavaScript practices and ensure proper error handling.""",
            
            "java": """
You specialize in Java development.
When creating Java files, use the .java extension and follow proper package structure.
Follow Java naming conventions and object-oriented design principles.""",

            "game": """
You specialize in game development.
When creating game files, follow common game architecture patterns.
Consider performance, game loop structure, asset management, and user interaction.
Implement clean separation between game logic, rendering, and input handling."""
        }
        
        return base_message + project_messages.get(project_type.lower(), "")
    
    return AssistantAgent(
        name="Coder",
        llm_config=llm_config,
        system_message=get_system_message(project_type)
    )

def get_reviewer_agent(config: Dict[str, Any]):
    """
    Create a Reviewer Agent that reviews code
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        AssistantAgent: The reviewer agent
    """
    # Create LLM client and get configuration
    llm_client = create_llm_client(config)
    llm_config = llm_client.get_autogen_config()
    # Use lower temperature for code review for more consistent feedback
    llm_config["temperature"] = 0.1
    
    system_message = """You are a Code Review Expert.

Your job is to review code and provide constructive feedback. Focus on:

1. Code correctness and logic errors
2. Performance issues and optimization opportunities
3. Security vulnerabilities
4. Adherence to best practices and design patterns
5. Code style and consistency
6. Readability and maintainability
7. Test coverage and edge cases

For each issue found:
- Describe the issue clearly
- Explain why it's a problem
- Suggest a specific solution with code examples
- Categorize issues by severity (critical, major, minor)

Always provide balanced feedback that includes both strengths and areas for improvement.
"""
    
    return AssistantAgent(
        name="Reviewer",
        llm_config=llm_config,
        system_message=system_message
    )

def get_test_agent(config: Dict[str, Any]):
    """
    Create a Test Agent that writes and executes tests
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        AssistantAgent: The test agent
    """
    llm_config = {
        "model": config.get("llm", {}).get("model", "gpt-4"),
        "temperature": config.get("llm", {}).get("temperature", 0.2),
        "max_tokens": config.get("llm", {}).get("max_tokens", 2000),
    }
    
    system_message = """You are a Testing Expert.

Your primary responsibility is to create comprehensive test suites for code. You focus on:

1. Unit tests for individual functions/methods
2. Integration tests for component interactions
3. End-to-end tests for complete workflows
4. Edge case testing and input validation
5. Performance and load testing when relevant

When writing tests:
- Create descriptive test names that explain the scenario being tested
- Follow the Arrange-Act-Assert pattern
- Ensure adequate coverage of code branches
- Use appropriate testing frameworks for the language/environment
- Implement mocks/stubs for external dependencies
- Generate test data that exercises various conditions

You can both write new tests and evaluate existing test coverage.
"""
    
    return AssistantAgent(
        name="Tester",
        llm_config=llm_config,
        system_message=system_message
    )

def get_devops_agent(config: Dict[str, Any]):
    """
    Create a DevOps Agent that sets up CI/CD or Docker
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        AssistantAgent: The devops agent
    """
    llm_config = {
        "model": config.get("llm", {}).get("model", "gpt-4"),
        "temperature": config.get("llm", {}).get("temperature", 0.2),
        "max_tokens": config.get("llm", {}).get("max_tokens", 2000),
    }
    
    system_message = """You are a DevOps Expert.

Your primary responsibilities include:

1. Setting up CI/CD pipelines (GitHub Actions, Jenkins, CircleCI, etc.)
2. Creating Docker configurations for containerization
3. Configuring deployment environments
4. Establishing testing automation within pipelines
5. Implementing infrastructure-as-code
6. Setting up monitoring and logging
7. Ensuring security best practices in build/deployment

When given a project, you can:
- Create appropriate CI/CD configuration files
- Generate Dockerfiles and docker-compose configurations
- Script deployment processes
- Configure environment variables and secrets management
- Establish artifact repositories and versioning
- Set up branch protection and code quality gates

Always follow security best practices and ensure reproducible builds.
"""
    
    return AssistantAgent(
        name="DevOps",
        llm_config=llm_config,
        system_message=system_message
    )

def get_documentation_agent(config: Dict[str, Any]):
    """
    Create a Documentation Agent that generates README, comments, docstrings
    
    Args:
        config (dict): Configuration dictionary
    
    Returns:
        AssistantAgent: The documentation agent
    """
    llm_config = {
        "model": config.get("llm", {}).get("model", "gpt-4"),
        "temperature": config.get("llm", {}).get("temperature", 0.3),
        "max_tokens": config.get("llm", {}).get("max_tokens", 2000),
    }
    
    system_message = """You are a Documentation Expert.

Your primary responsibility is to create clear, comprehensive documentation for code. You focus on:

1. Writing project README files with setup instructions and usage examples
2. Adding inline code comments explaining complex logic
3. Creating function/method docstrings with parameters, return values, and examples
4. Developing user guides and API documentation
5. Documenting architectural decisions and design patterns used

When creating documentation:
- Use clear, concise language accessible to the target audience
- Include code examples that demonstrate usage
- Explain not just WHAT the code does, but WHY certain approaches were chosen
- Follow documentation standards for the language/framework (e.g., JSDoc, Sphinx)
- Ensure documentation is kept in sync with code changes

Your goal is to make codebases more approachable, maintainable, and usable.
"""
    
    return AssistantAgent(
        name="Documentation",
        llm_config=llm_config,
        system_message=system_message
    )
