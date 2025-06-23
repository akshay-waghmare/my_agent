"""
Enhanced file operations for the AutoGen Coding Agent.

This module extends the basic file operations with project-aware
functionality, automatic file type detection, and advanced features.
"""

import os
from pathlib import Path
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Union

def detect_file_type(file_path: str) -> str:
    """
    Detect the type of file based on extension and contents
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: File type ('python', 'javascript', 'html', 'css', etc.)
    """
    # Get the file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Map extensions to file types
    extension_map = {
        '.py': 'python',
        '.ipynb': 'jupyter',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react-typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.md': 'markdown',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c-header',
        '.hpp': 'cpp-header',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.cs': 'csharp',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.sql': 'sql',
        '.sh': 'shell',
        '.bat': 'batch',
        '.ps1': 'powershell',
    }
    
    return extension_map.get(ext, 'text')

def create_file_with_checks(file_path: str, content: str) -> str:
    """
    Create a new file with content validation and directory creation
    
    Args:
        file_path: Path to the file to create
        content: Content to write to the file
        
    Returns:
        str: Success message or error message
    """
    try:
        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Check if file already exists
        if os.path.exists(file_path):
            return f"File {file_path} already exists. Use write_file() to overwrite or apply_diff() to modify."
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Detect file type
        file_type = detect_file_type(file_path)
        
        # Validate content based on file type
        if file_type == 'python' and not content.strip():
            return f"Error: Cannot create empty Python file {file_path}"
        
        if file_type == 'json':
            try:
                # Attempt to parse JSON to validate
                json.loads(content)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON content for {file_path}"
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully created {file_path} ({file_type} file)"
    except Exception as e:
        return f"Error creating {file_path}: {e}"

def read_file_with_context(file_path: str, context_lines: int = 0) -> Dict[str, Any]:
    """
    Read a file and return content with metadata and context
    
    Args:
        file_path: Path to the file to read
        context_lines: Number of lines of context to include
        
    Returns:
        Dict: File content, metadata, and context
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File {file_path} does not exist"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get file metadata
        file_stat = os.stat(file_path)
        file_type = detect_file_type(file_path)
        
        result = {
            "content": content,
            "metadata": {
                "path": file_path,
                "size": file_stat.st_size,
                "modified": file_stat.st_mtime,
                "type": file_type,
                "exists": True
            },
        }
        
        # Add context from related files if requested
        if context_lines > 0:
            result["context"] = get_file_context(file_path, context_lines)
            
        return result
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            return {
                "content": content,
                "metadata": {
                    "path": file_path,
                    "size": os.stat(file_path).st_size,
                    "modified": os.stat(file_path).st_mtime,
                    "type": detect_file_type(file_path),
                    "exists": True,
                    "encoding": "latin-1"
                }
            }
        except Exception as e:
            return {"error": f"Error reading {file_path}: {e}"}
    except Exception as e:
        return {"error": f"Error reading {file_path}: {e}"}

def get_file_context(file_path: str, context_lines: int = 3) -> List[Dict[str, Any]]:
    """
    Get context information for a file (imports, related files)
    
    Args:
        file_path: Path to the file
        context_lines: Number of context lines to include
        
    Returns:
        List[Dict]: List of related files with context
    """
    # Implementation would search for related files based on imports, etc.
    # For now, just return files in the same directory
    context = []
    try:
        directory = os.path.dirname(file_path)
        for f in os.listdir(directory):
            if f != os.path.basename(file_path):
                context_file_path = os.path.join(directory, f)
                if os.path.isfile(context_file_path):
                    with open(context_file_path, 'r', encoding='utf-8', errors='ignore') as cf:
                        lines = cf.readlines()[:context_lines]
                    context.append({
                        "path": context_file_path,
                        "preview": "".join(lines),
                        "type": detect_file_type(context_file_path)
                    })
    except Exception as e:
        # If we can't get context, just return an empty list
        pass
    
    return context

def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """
    Find files matching a pattern in a directory
    
    Args:
        directory: Base directory to search
        pattern: Pattern to match (glob syntax)
        
    Returns:
        List[str]: List of matching file paths
    """
    from glob import glob
    import os
    
    # Make directory absolute if it's not
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    
    # Join the directory with the pattern
    pattern_path = os.path.join(directory, pattern)
    
    # Find the files
    return glob(pattern_path, recursive=True)

def analyze_project_structure(directory: str) -> Dict[str, Any]:
    """
    Analyze a project directory to determine language, structure, etc.
    
    Args:
        directory: Project directory path
        
    Returns:
        Dict: Project analysis information
    """
    if not os.path.exists(directory):
        return {"error": f"Directory {directory} does not exist"}
    
    # Count file types
    file_counts = {}
    total_files = 0
    
    # Check for common project files
    has_package_json = os.path.exists(os.path.join(directory, 'package.json'))
    has_requirements_txt = os.path.exists(os.path.join(directory, 'requirements.txt'))
    has_pyproject_toml = os.path.exists(os.path.join(directory, 'pyproject.toml'))
    has_cargo_toml = os.path.exists(os.path.join(directory, 'Cargo.toml'))
    has_gemfile = os.path.exists(os.path.join(directory, 'Gemfile'))
    has_pom_xml = os.path.exists(os.path.join(directory, 'pom.xml'))
    has_go_mod = os.path.exists(os.path.join(directory, 'go.mod'))
    
    # Walk the directory and count file types
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_type = detect_file_type(file_path)
            file_counts[file_type] = file_counts.get(file_type, 0) + 1
            total_files += 1
    
    # Determine main language
    main_language = max(file_counts.items(), key=lambda x: x[1])[0] if file_counts else "unknown"
    
    # Determine project type
    project_type = "generic"
    if has_package_json:
        if file_counts.get('react', 0) > 0:
            project_type = "react"
        elif file_counts.get('typescript', 0) > 0:
            project_type = "typescript"
        else:
            project_type = "javascript"
    elif has_requirements_txt or has_pyproject_toml:
        project_type = "python"
    elif has_cargo_toml:
        project_type = "rust"
    elif has_gemfile:
        project_type = "ruby"
    elif has_pom_xml:
        project_type = "java"
    elif has_go_mod:
        project_type = "go"
    elif file_counts.get('html', 0) > 0 and file_counts.get('css', 0) > 0:
        project_type = "web"
    
    return {
        "main_language": main_language,
        "project_type": project_type,
        "file_counts": file_counts,
        "total_files": total_files,
        "package_manager": {
            "npm": has_package_json,
            "pip": has_requirements_txt,
            "poetry": has_pyproject_toml,
            "cargo": has_cargo_toml,
            "bundler": has_gemfile,
            "maven": has_pom_xml,
            "go": has_go_mod
        }
    }

# Export enhanced functions to replace or supplement the basic ones
__all__ = [
    'create_file_with_checks', 
    'read_file_with_context', 
    'detect_file_type', 
    'find_files_by_pattern',
    'analyze_project_structure',
    'get_file_context'
]
