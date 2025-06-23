"""
File operations utilities for the AutoGen Coding Agent.
This module provides functions for reading and writing files, as well as applying code diffs.
"""

import os
from pathlib import Path
import re

def read_file(file_path: str) -> str:
    """
    Read content from a file
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: File content or error message
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"Error reading {file_path}: {e}"
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file
    
    Args:
        file_path (str): Path to the file to write
        content (str): Content to write to the file
        
    Returns:
        str: Success message or error message
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to {file_path}: {e}"

def create_file(file_path: str, content: str) -> str:
    """
    Create a new file with the specified content
    
    Args:
        file_path (str): Path to the file to create
        content (str): Content to write to the file
        
    Returns:
        str: Success message or error message
    """
    try:
        # Check if file already exists
        if os.path.exists(file_path):
            return f"File {file_path} already exists. Use write_file() to overwrite or apply_diff() to modify."
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created {file_path}"
    except Exception as e:
        return f"Error creating {file_path}: {e}"

def apply_code_diff(file_path: str, diff_content: str) -> bool:
    """
    Apply a code diff to a file
    
    Args:
        file_path (str): Path to the file to modify
        diff_content (str): Diff content to apply
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read().splitlines()
        
        # Parse the diff content
        # This is a simple implementation that can be enhanced in future
        updated_content = original_content.copy()
        lines = diff_content.split('\n')
        
        # Track line offsets as we add or remove lines
        line_offset = 0
        
        for i, line in enumerate(lines):
            if line.startswith('- '):
                # Find and remove this line
                old_line = line[2:]
                if old_line in updated_content:
                    line_index = updated_content.index(old_line)
                    updated_content.pop(line_index)
                    line_offset -= 1
            elif line.startswith('+ '):
                # Add this line after the previous non-removal line
                new_line = line[2:]
                
                # Try to find position based on context
                context_found = False
                if i > 0 and not lines[i-1].startswith('- ') and not lines[i-1].startswith('+ '):
                    context_line = lines[i-1]
                    if context_line in updated_content:
                        line_index = updated_content.index(context_line)
                        updated_content.insert(line_index + 1, new_line)
                        line_offset += 1
                        context_found = True
                
                if not context_found:
                    # If no context, append to the end
                    updated_content.append(new_line)
                    line_offset += 1
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_content))
        
        print(f"Successfully applied diff to {file_path}")
        return True
    
    except Exception as e:
        print(f"Error applying diff to {file_path}: {e}")
        return False

def load_tasks(tasks_file: str = "tasks.md") -> str:
    """
    Load tasks from tasks.md file
    
    Args:
        tasks_file (str): Path to the tasks file, defaults to tasks.md in agent directory
        
    Returns:
        str: Content of the tasks file or a message if not found
    """
    if not os.path.isabs(tasks_file):
        # If relative path, assume it's relative to the agent directory
        tasks_path = Path(__file__).parent.parent / tasks_file
    else:
        tasks_path = Path(tasks_file)
    
    if not tasks_path.exists():
        return f"No tasks file found at {tasks_path}"
    
    with open(tasks_path, 'r', encoding='utf-8') as f:
        return f.read()
