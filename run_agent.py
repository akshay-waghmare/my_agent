"""
AutoGen Coding Agent Runner

Simple runner script to start the coding agent.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the agent
from agent.code_agent import main

if __name__ == "__main__":
    main()
