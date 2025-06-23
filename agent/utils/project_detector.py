"""
Project Type Detection Module

This module provides functions for automatically detecting project types,
languages, and frameworks based on file structure and content.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

def detect_project_type(directory: str) -> Dict[str, Any]:
    """
    Detect the type of project in a directory
    
    Args:
        directory: Project directory path
        
    Returns:
        Dict: Project type information
    """
    if not os.path.exists(directory):
        return {"error": f"Directory {directory} does not exist"}
    
    # Check for key project files
    has_package_json = os.path.exists(os.path.join(directory, 'package.json'))
    has_requirements_txt = os.path.exists(os.path.join(directory, 'requirements.txt'))
    has_setup_py = os.path.exists(os.path.join(directory, 'setup.py'))
    has_pyproject_toml = os.path.exists(os.path.join(directory, 'pyproject.toml'))
    has_gemfile = os.path.exists(os.path.join(directory, 'Gemfile'))
    has_cargo_toml = os.path.exists(os.path.join(directory, 'Cargo.toml'))
    has_go_mod = os.path.exists(os.path.join(directory, 'go.mod'))
    has_pom_xml = os.path.exists(os.path.join(directory, 'pom.xml'))
    has_build_gradle = os.path.exists(os.path.join(directory, 'build.gradle'))
    has_swift_package = os.path.exists(os.path.join(directory, 'Package.swift'))
    has_index_html = os.path.exists(os.path.join(directory, 'index.html'))
    
    # Check for framework-specific files
    has_react = has_package_json and _check_file_for_content(
        os.path.join(directory, 'package.json'), 
        ['react', 'react-dom', 'react-native']
    )
    has_vue = has_package_json and _check_file_for_content(
        os.path.join(directory, 'package.json'),
        ['vue']
    )
    has_angular = has_package_json and _check_file_for_content(
        os.path.join(directory, 'package.json'),
        ['@angular/core']
    )
    has_next = has_package_json and _check_file_for_content(
        os.path.join(directory, 'package.json'),
        ['next']
    )
    has_django = _check_for_file(directory, 'manage.py') and _check_for_file(directory, 'settings.py')
    has_flask = has_requirements_txt and _check_file_for_content(
        os.path.join(directory, 'requirements.txt'),
        ['flask']
    )
    has_fastapi = has_requirements_txt and _check_file_for_content(
        os.path.join(directory, 'requirements.txt'),
        ['fastapi']
    )
    has_rails = has_gemfile and _check_file_for_content(
        os.path.join(directory, 'Gemfile'),
        ['rails']
    )
    
    # Count files by extension
    extension_counts = count_file_extensions(directory)
    
    # Determine project type
    if has_react:
        project_type = "react"
        if has_next:
            project_type = "nextjs"
    elif has_vue:
        project_type = "vue"
    elif has_angular:
        project_type = "angular"
    elif has_django:
        project_type = "django"
    elif has_flask:
        project_type = "flask"
    elif has_fastapi:
        project_type = "fastapi"
    elif has_rails:
        project_type = "rails"
    elif has_package_json:
        if extension_counts.get('.ts', 0) > extension_counts.get('.js', 0):
            project_type = "typescript"
        else:
            project_type = "javascript"
    elif has_requirements_txt or has_setup_py or has_pyproject_toml:
        project_type = "python"
    elif has_cargo_toml:
        project_type = "rust"
    elif has_go_mod:
        project_type = "go"
    elif has_pom_xml or has_build_gradle:
        project_type = "java"
    elif has_swift_package:
        project_type = "swift"
    elif has_gemfile:
        project_type = "ruby"
    elif has_index_html and extension_counts.get('.html', 0) > 0:
        project_type = "web"
    elif extension_counts.get('.cs', 0) > 0:
        project_type = "csharp"
    elif extension_counts.get('.cpp', 0) > 0 or extension_counts.get('.c', 0) > 0:
        project_type = "cpp"
    else:
        # Try to determine by dominant file type
        dominant_ext = max(extension_counts.items(), key=lambda x: x[1])[0] if extension_counts else None
        if dominant_ext == '.py':
            project_type = "python"
        elif dominant_ext == '.js':
            project_type = "javascript"
        elif dominant_ext == '.ts':
            project_type = "typescript"
        elif dominant_ext == '.html' or dominant_ext == '.css':
            project_type = "web"
        elif dominant_ext == '.java':
            project_type = "java"
        elif dominant_ext == '.cs':
            project_type = "csharp"
        elif dominant_ext == '.go':
            project_type = "go"
        else:
            project_type = "generic"
    
    # Determine if this is a game
    is_game = (
        _check_for_directory(directory, 'assets') and 
        (_check_for_directory(directory, 'sprites') or _check_for_directory(directory, 'textures') or 
         _check_for_directory(directory, 'models')) or
        _check_for_file(directory, 'game.js') or
        _check_for_file(directory, 'game.py') or
        _check_for_file(directory, 'game.ts')
    )
    
    if is_game:
        project_type = f"{project_type}-game"
    
    # Determine language type (even if we couldn't determine framework)
    main_language = "unknown"
    if extension_counts:
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c-header',
            '.hpp': 'cpp-header'
        }
        
        # Find the extension with the most files
        main_ext = max(extension_counts.items(), key=lambda x: x[1])[0] if extension_counts else None
        if main_ext in ext_to_lang:
            main_language = ext_to_lang[main_ext]
    
    return {
        "project_type": project_type,
        "main_language": main_language,
        "frameworks": {
            "react": has_react,
            "vue": has_vue,
            "angular": has_angular,
            "next": has_next,
            "django": has_django,
            "flask": has_flask,
            "fastapi": has_fastapi,
            "rails": has_rails
        },
        "package_managers": {
            "npm": has_package_json,
            "pip": has_requirements_txt,
            "poetry": has_pyproject_toml,
            "cargo": has_cargo_toml,
            "go": has_go_mod,
            "maven": has_pom_xml,
            "gradle": has_build_gradle,
            "swift": has_swift_package,
            "bundler": has_gemfile
        },
        "file_stats": {
            "extension_counts": extension_counts,
            "total_files": sum(extension_counts.values())
        },
        "is_game": is_game,
        "is_web": project_type in ["web", "react", "vue", "angular", "nextjs"]
    }

def count_file_extensions(directory: str) -> Dict[str, int]:
    """
    Count files by extension in a directory
    
    Args:
        directory: Directory to analyze
        
    Returns:
        Dict: Dictionary with extension counts
    """
    extension_counts = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            # Get the file extension
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # Increment the count for this extension
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
    
    return extension_counts

def _check_file_for_content(file_path: str, search_strings: List[str]) -> bool:
    """
    Check if a file contains any of the search strings
    
    Args:
        file_path: Path to the file
        search_strings: List of strings to search for
        
    Returns:
        bool: True if any search string is found
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            for search_str in search_strings:
                if search_str in content:
                    return True
    except:
        # If there's any error, just return False
        pass
    
    return False

def _check_for_file(directory: str, filename: str) -> bool:
    """
    Check if a file exists anywhere in a directory tree
    
    Args:
        directory: Base directory to search
        filename: Filename to look for
        
    Returns:
        bool: True if file is found
    """
    for root, _, files in os.walk(directory):
        if filename in files:
            return True
    return False

def _check_for_directory(directory: str, dirname: str) -> bool:
    """
    Check if a directory exists anywhere in a directory tree
    
    Args:
        directory: Base directory to search
        dirname: Directory name to look for
        
    Returns:
        bool: True if directory is found
    """
    for root, dirs, _ in os.walk(directory):
        if dirname in dirs:
            return True
    return False

def get_project_system_message(project_info: Dict[str, Any]) -> str:
    """
    Generate a specialized system message for a project type
    
    Args:
        project_info: Project type information from detect_project_type
        
    Returns:
        str: Specialized system message for the project type
    """
    project_type = project_info["project_type"]
    main_language = project_info["main_language"]
    
    # Base system message
    base_message = """You are an expert coding assistant that can create, read, and modify files.

Your capabilities:
1. CREATE FILES: Call create_file(path, content) to create new files
2. READ FILES: Call file_reader(path) to read existing files  
3. MODIFY FILES: Call apply_diff(path, diff) to apply changes to existing files

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
- Follow modern development best practices
- Include comprehensive comments in your code

Be proactive - when asked to create files, actually create them using function calls."""

    # Project-specific additions
    project_messages = {
        "python": """
You specialize in Python development.
When creating Python files, use the .py extension.
Follow PEP 8 style guidelines and include appropriate docstrings.
Consider including tests for your code when appropriate.""",
            
        "django": """
You specialize in Django web development.
Follow Django's MVT (Model-View-Template) architecture.
Create appropriate models, views, templates, and URL configurations.
Follow Django best practices for project structure and code organization.""",
            
        "flask": """
You specialize in Flask web development.
Organize code using application factories and blueprints when appropriate.
Include appropriate route handlers and templates.
Follow Flask best practices for project structure.""",
            
        "javascript": """
You specialize in JavaScript/TypeScript development.
When creating JavaScript files, use the .js extension.
Use modern JavaScript features (ES6+) with appropriate polyfills if needed.
Follow JavaScript best practices and ensure proper error handling.""",
            
        "typescript": """
You specialize in TypeScript development.
When creating TypeScript files, use the .ts extension.
Utilize TypeScript's type system effectively for better code quality.
Follow TypeScript best practices and design patterns.""",
            
        "react": """
You specialize in React development.
Create reusable components with proper props and state management.
Use functional components with hooks rather than class components.
Follow React best practices for code organization and performance.""",
            
        "nextjs": """
You specialize in Next.js development.
Utilize Next.js features like Server Components, API routes, and app router.
Follow the appropriate directory structure and file naming conventions.
Implement proper data fetching strategies and page routing.""",
            
        "vue": """
You specialize in Vue.js development.
Create reusable components with proper props and emits.
Follow Vue.js conventions for component structure and lifecycle methods.
Implement proper state management using Composition API or Vuex.""",
            
        "angular": """
You specialize in Angular development.
Follow Angular's component architecture and module system.
Utilize Angular services, directives, and pipes appropriately.
Implement proper state management and follow Angular style guidelines.""",
            
        "java": """
You specialize in Java development.
Follow object-oriented design principles and Java naming conventions.
Create appropriate package structure and class hierarchy.
Include proper exception handling and follow Java best practices.""",
            
        "web": """
You specialize in web development using HTML, CSS, and JavaScript.
Create responsive and accessible web interfaces.
Follow semantic HTML practices and modern CSS techniques.
Ensure cross-browser compatibility and performance optimization.""",
            
        "rust": """
You specialize in Rust development.
Leverage Rust's ownership system for memory safety.
Write idiomatic Rust code following community guidelines.
Include appropriate error handling with Result and Option types.""",
            
        "go": """
You specialize in Go development.
Follow Go's idiomatic approach to code organization.
Use appropriate error handling and concurrency patterns.
Follow Go's naming conventions and code formatting standards.""",
            
        "csharp": """
You specialize in C# development.
Follow object-oriented design principles and .NET conventions.
Utilize appropriate language features and LINQ when beneficial.
Follow C# coding standards and best practices.""",
            
        "cpp": """
You specialize in C++ development.
Follow modern C++ practices (C++11 and newer) when appropriate.
Include proper memory management and resource handling.
Follow established C++ coding standards and design patterns.""",
            
        "swift": """
You specialize in Swift development.
Follow Swift's design patterns and coding conventions.
Utilize Swift's type system and optionals effectively.
Follow Swift best practices for API design and memory management.""",
            
        "ruby": """
You specialize in Ruby development.
Follow Ruby's idiomatic coding style and conventions.
Apply object-oriented design principles appropriate for Ruby.
Follow Ruby best practices and community guidelines.""",
            
        "rails": """
You specialize in Ruby on Rails development.
Follow Rails conventions for MVC architecture and RESTful routes.
Utilize Rails' built-in features for common tasks.
Follow Rails best practices for code organization and security."""
    }
    
    # Add game development additions if relevant
    if project_info.get("is_game", False):
        game_message = """
You also specialize in game development.
Consider game architecture patterns like Entity-Component Systems when appropriate.
Pay attention to performance and game loop structures.
Implement clean separation between game logic, rendering, and input handling."""
        
        if project_type in project_messages:
            project_messages[project_type] += game_message
        else:
            project_messages["generic-game"] = game_message
    
    # Use the main language message if we have a specialized one
    main_language_lower = main_language.lower()
    if project_type not in project_messages and main_language_lower in project_messages:
        project_specific = project_messages[main_language_lower]
    else:
        project_specific = project_messages.get(project_type, "")
    
    return base_message + project_specific

# Export functions
__all__ = [
    'detect_project_type',
    'count_file_extensions',
    'get_project_system_message'
]
