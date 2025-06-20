"""
Git Integration Extension for AutoGen Coding Agent

This extension adds Git functionality to the coding agent.
"""

import subprocess
import os
from pathlib import Path

def git_init(repo_path="."):
    """
    Initialize a git repository
    
    Args:
        repo_path (str): Path to the repository directory
        
    Returns:
        str: Success message or error message
    """
    try:
        result = subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return f"Git repository initialized in {repo_path}"
    except subprocess.CalledProcessError as e:
        return f"Error initializing git repository: {e.stderr}"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"

def git_add(files, repo_path="."):
    """
    Add files to git staging area
    
    Args:
        files (str or list): File(s) to add
        repo_path (str): Path to the repository directory
        
    Returns:
        str: Success message or error message
    """
    try:
        if isinstance(files, str):
            files = [files]
        
        for file in files:
            result = subprocess.run(
                ["git", "add", file],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
        
        return f"Added {len(files)} file(s) to git staging area"
    except subprocess.CalledProcessError as e:
        return f"Error adding files to git: {e.stderr}"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"

def git_commit(message, repo_path="."):
    """
    Commit changes to git repository
    
    Args:
        message (str): Commit message
        repo_path (str): Path to the repository directory
        
    Returns:
        str: Success message or error message
    """
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return f"Committed changes with message: '{message}'"
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr:
            return "No changes to commit"
        return f"Error committing to git: {e.stderr}"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"

def git_status(repo_path="."):
    """
    Get git repository status
    
    Args:
        repo_path (str): Path to the repository directory
        
    Returns:
        str: Git status output or error message
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            return f"Git status:\n{result.stdout}"
        else:
            return "Working tree clean"
            
    except subprocess.CalledProcessError as e:
        return f"Error getting git status: {e.stderr}"
    except FileNotFoundError:
        return "Error: Git is not installed or not in PATH"

def auto_commit_changes(file_path, commit_message=None, repo_path="."):
    """
    Automatically add and commit a file
    
    Args:
        file_path (str): Path to the file to commit
        commit_message (str, optional): Commit message. If None, auto-generates one.
        repo_path (str): Path to the repository directory
        
    Returns:
        str: Success message or error message
    """
    if commit_message is None:
        filename = Path(file_path).name
        commit_message = f"AutoGen: Updated {filename}"
    
    # Add the file
    add_result = git_add(file_path, repo_path)
    if "Error" in add_result:
        return add_result
    
    # Commit the changes
    commit_result = git_commit(commit_message, repo_path)
    return f"{add_result}\n{commit_result}"

# Function map for integration with the agent
GIT_FUNCTION_MAP = {
    "git_init": git_init,
    "git_add": git_add,
    "git_commit": git_commit,
    "git_status": git_status,
    "auto_commit_changes": auto_commit_changes
}
