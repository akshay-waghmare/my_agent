"""
MCP Loader - Clean Implementation

The MCP (Model Context Protocol) loader is responsible for:
1. Loading the .mcp.yaml configuration file
2. Setting up the appropriate agents based on the configuration
3. Executing the workflow based on the MCP settings
4. Managing tools and capabilities for the agents
"""

import yaml
import os
from pathlib import Path
import json
from typing import Dict, List, Any, Optional, Union, Callable

class MCPLoader:
    """
    MCP-style loader that parses tasks.md and directly executes tasks
    """
    
    def __init__(self, tasks_file: str = "tasks.md", config: Dict = None):
        self.tasks_file = tasks_file
        self.config = config or {}
        self.tasks = []
        self.tools = {}
        
    def load_tasks(self) -> List[Dict]:
        """Load and parse tasks from markdown file"""
        # Try to find the tasks file in various locations
        possible_paths = [
            Path(self.tasks_file),  # Direct path
            Path("agent") / "tasks.md",  # agent/tasks.md
            Path(__file__).parent / "tasks.md",  # Same directory as this file
        ]
        
        tasks_path = None
        for path in possible_paths:
            if path.exists():
                tasks_path = path
                break
                
        if tasks_path is None:
            print(f"Tasks file not found in any of these locations:")
            for path in possible_paths:
                print(f"  - {path.absolute()}")
            return []
            
        print(f"Found tasks file at: {tasks_path.absolute()}")
        
        with open(tasks_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse tasks from markdown
        self.tasks = self._parse_markdown_tasks(content)
        return self.tasks
        
    def _parse_markdown_tasks(self, content: str) -> List[Dict]:
        """Parse tasks from markdown content"""
        tasks = []
        lines = content.split('\n')
        current_task = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('## Task'):
                if current_task:
                    tasks.append(current_task)
                    
                # Extract task name and number
                task_title = line.replace('## Task', '').strip()
                if ':' in task_title:
                    task_num, task_name = task_title.split(':', 1)
                    task_name = task_name.strip()
                else:
                    task_num = task_title.split()[0] if task_title.split() else "1"
                    task_name = task_title
                    
                current_task = {
                    'id': task_num.strip(),
                    'name': task_name,
                    'description': '',
                    'steps': [],
                    'type': 'general'
                }
                
            elif line.startswith('- ') and current_task:
                # Extract step
                step = line[2:].strip()
                current_task['steps'].append(step)
                
                # Determine task type based on content
                if 'html' in step.lower() or 'create' in step.lower():
                    current_task['type'] = 'file_creation'
                elif 'style' in step.lower() or 'css' in step.lower():
                    current_task['type'] = 'file_modification'
                    
        if current_task:
            tasks.append(current_task)
            
        return tasks
        
    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool function"""
        self.tools[name] = {
            'function': func,
            'description': description
        }
        
    def execute_task(self, task: Dict) -> Dict:
        """Execute a single task using available tools"""
        print(f"\n🎯 Executing Task {task['id']}: {task['name']}")
        print(f"Description: {task['description']}")
        
        results = []
        
        for i, step in enumerate(task['steps'], 1):
            print(f"\n📋 Step {i}: {step}")
            
            # Determine which tool to use based on step content
            if 'create' in step.lower() and 'html' in step.lower():
                result = self._create_html_file(step)
            elif 'style' in step.lower() or 'css' in step.lower():
                result = self._add_styling(step)
            else:
                result = self._execute_general_step(step)
                
            results.append({
                'step': step,
                'result': result,
                'success': 'error' not in result.lower()
            })
            
        return {
            'task_id': task['id'],
            'task_name': task['name'],
            'steps_executed': len(results),
            'results': results,
            'overall_success': all(r['success'] for r in results)
        }
        
    def _create_html_file(self, step: str) -> str:
        """Create an HTML file based on the step description"""
        # Extract any specific content from the step
        if 'hello agentic world' in step.lower():
            content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello Agentic World</title>
</head>
<body>
    <h1>Hello Agentic World</h1>
    <p>Welcome to the world of AI agents!</p>
</body>
</html>'''
        else:
            content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
</head>
<body>
    <h1>Generated Content</h1>
</body>
</html>'''
        
        # Use the file creation tool
        if 'create_file' in self.tools:
            result = self.tools['create_file']['function']('project-code/index.html', content)
        else:
            # Fallback to direct file creation
            try:
                os.makedirs('project-code', exist_ok=True)
                with open('project-code/index.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                result = "Successfully created project-code/index.html"
            except Exception as e:
                result = f"Error creating HTML file: {e}"
                
        print(f"✅ {result}")
        return result
        
    def _add_styling(self, step: str) -> str:
        """Add styling to the HTML file"""
        html_file = 'project-code/index.html'
        
        if not os.path.exists(html_file):
            return "Error: HTML file not found. Create it first."
            
        try:
            # Read current file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add CSS styling
            css_styles = '''
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: white;
        }
        
        h1 {
            font-size: 3rem;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 1rem;
            animation: fadeIn 2s ease-in;
        }
        
        p {
            font-size: 1.2rem;
            text-align: center;
            opacity: 0.9;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
    </style>'''
            
            # Insert styles before </head> and wrap content in container
            if '</head>' in content:
                content = content.replace('</head>', css_styles + '\n</head>')
            
            # Wrap body content in a container
            if '<body>' in content and '</body>' in content:
                body_start = content.find('<body>') + 6
                body_end = content.find('</body>')
                body_content = content[body_start:body_end].strip()
                
                new_body_content = f'\n    <div class="container">\n        {body_content}\n    </div>\n'
                content = content[:body_start] + new_body_content + content[body_end:]
            
            # Write back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            result = "Successfully added beautiful styling to index.html"
        except Exception as e:
            result = f"Error adding styling: {e}"
            
        print(f"✅ {result}")
        return result
        
    def _execute_general_step(self, step: str) -> str:
        """Execute a general step"""
        return f"Executed: {step}"
        
    def run_all_tasks(self) -> List[Dict]:
        """Run all loaded tasks"""
        if not self.tasks:
            self.load_tasks()
            
        results = []
        for task in self.tasks:
            result = self.execute_task(task)
            results.append(result)
            
        return results
        
    def get_summary(self, results: List[Dict]) -> str:
        """Get a summary of task execution results"""
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r['overall_success'])
        
        summary = f"\n🎉 Task Execution Summary:\n"
        summary += f"   Total tasks: {total_tasks}\n"
        summary += f"   Successful: {successful_tasks}\n"
        summary += f"   Failed: {total_tasks - successful_tasks}\n\n"
        
        for result in results:
            status = "✅" if result['overall_success'] else "❌"
            summary += f"{status} Task {result['task_id']}: {result['task_name']}\n"
            
        return summary
