"""
MCP (Model Context Protocol) Style Loader for AutoGen Coding Agent

This module implements an MCP-like approach for loading tasks and tools,
then dynamically feeding them into AutoGen agents with full LLM integration.
"""

import yaml
import os
import requests
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Callable

class MCPLoader:
    """
    MCP-style loader that parses tasks.md and dynamically configures agents
    """
    
    def __init__(self, tasks_file: str = "tasks.md", config: Dict = None):
        self.tasks_file = tasks_file
        self.config = config or {}
        self.tasks = []
        self.tools = {}
        self.constraints = []
        self.goals = []
        
        # Initialize LLM settings from config
        self.llm_config = self.config.get('llm', {
            'provider': 'lmstudio',
            'temperature': 0.2,
            'max_tokens': 2000
        })
        
    def load_tasks(self) -> List[Dict]:
        """Load and parse tasks from markdown file"""
        if not os.path.isabs(self.tasks_file):
            # If relative path, check both current directory and agent directory
            possible_paths = [
                Path(self.tasks_file),  # Direct relative path
                Path("agent") / "tasks.md",  # agent/tasks.md
                Path(__file__).parent / "tasks.md",  # Same directory as this file
                Path(__file__).parent.parent / "agent" / "tasks.md"  # project_root/agent/tasks.md
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
        else:
            tasks_path = Path(self.tasks_file)
            
        print(f"Found tasks file at: {tasks_path.absolute()}")
            
        if not tasks_path.exists():
            print(f"Tasks file not found: {tasks_path}")
            return []
            
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
                    
            elif line and current_task and not line.startswith('#'):
                # Add to description
                current_task['description'] += line + ' '
                
        if current_task:
            tasks.append(current_task)
            
        return tasks
        
    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool function"""
        self.tools[name] = {
            'function': func,
            'description': description
        }
        
    def register_tools_from_module(self, module_functions: Dict[str, Callable]):
        """Register multiple tools from a module"""
        for name, func in module_functions.items():
            self.register_tool(name, func, func.__doc__ or "")
    
    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM with the given prompt"""
        try:
            if self.llm_config['provider'] == 'lmstudio':
                response = requests.post(
                    "http://localhost:1234/v1/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "default",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": self.llm_config.get('temperature', 0.2),
                        "max_tokens": self.llm_config.get('max_tokens', 2000)
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"LLM API error: {response.status_code}")
                    return None
            else:
                print(f"Unsupported LLM provider: {self.llm_config['provider']}")
                return None
        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            return None
    
    def _extract_code_from_llm_response(self, response: str) -> str:
        """Extract code content from LLM response"""
        # Look for code blocks
        code_block_pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the response as-is (might be plain code)
        return response.strip()
            
    def execute_task(self, task: Dict) -> Dict:
        """Execute a single task using available tools and LLM reasoning"""
        print(f"\n🎯 Executing Task {task['id']}: {task['name']}")
        print(f"Description: {task['description']}")
        
        results = []
        
        for i, step in enumerate(task['steps'], 1):
            print(f"\n📋 Step {i}: {step}")
            
            # Use LLM to determine the best approach for each step
            if any(keyword in step.lower() for keyword in ['create', 'html', 'file']):
                if 'html' in step.lower():
                    result = self._create_html_file(step)
                else:
                    result = self._create_file_with_llm(step)
            elif any(keyword in step.lower() for keyword in ['style', 'css', 'design', 'appearance']):
                result = self._add_styling(step)
            elif any(keyword in step.lower() for keyword in ['javascript', 'js', 'script', 'interactive']):
                result = self._create_javascript_with_llm(step)
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
    
    def _create_file_with_llm(self, step: str) -> str:
        """Create any type of file based on the step description using LLM"""
        print(f"🤖 Using LLM to generate file content for: {step}")
        
        # Create a detailed prompt for the LLM
        prompt = f"""
You are an expert software developer. Create a complete file based on this requirement:

"{step}"

Requirements:
- Analyze the step to determine what type of file is needed
- Create complete, production-ready code
- Follow best practices for the file type
- Include proper comments and documentation
- Suggest an appropriate filename

Please provide:
1. The suggested filename
2. The complete file content

Format your response as:
filename: [suggested_filename]
```[language]
[complete code content]
```
"""
        
        # Get file content from LLM
        llm_response = self._call_llm(prompt)
        
        if not llm_response:
            return "Error: Failed to generate file content with LLM"
        
        # Extract filename and content
        filename_match = re.search(r'filename:\s*([^\n]+)', llm_response, re.IGNORECASE)
        filename = filename_match.group(1).strip() if filename_match else "generated_file.txt"
        
        # Extract code content
        file_content = self._extract_code_from_llm_response(llm_response)
        
        # Use the file creation tool
        filepath = f'project-code/{filename}'
        if 'create_file' in self.tools:
            result = self.tools['create_file']['function'](filepath, file_content)
        else:
            # Fallback to direct file creation
            try:
                os.makedirs('project-code', exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                result = f"Successfully created {filepath} with LLM-generated content"
            except Exception as e:
                result = f"Error creating file: {e}"
                
        print(f"✅ {result}")
        return result
    
    def _create_javascript_with_llm(self, step: str) -> str:
        """Create JavaScript file based on the step description using LLM"""
        print(f"🤖 Using LLM to generate JavaScript content for: {step}")
        
        # Create a detailed prompt for the LLM
        prompt = f"""
You are an expert JavaScript developer. Create a complete JavaScript file based on this requirement:

"{step}"

Requirements:
- Create modern, clean JavaScript code
- Follow best practices and ES6+ standards
- Include proper comments and documentation
- Ensure code is production-ready
- Make it compatible with modern browsers

Please provide ONLY the JavaScript code, no explanations or additional text.
"""
        
        # Get JavaScript content from LLM
        js_content = self._call_llm(prompt)
        
        if not js_content:
            return "Error: Failed to generate JavaScript content with LLM"
        
        # Extract code if it's wrapped in code blocks
        js_content = self._extract_code_from_llm_response(js_content)
        
        # Use the file creation tool
        filepath = 'project-code/script.js'
        if 'create_file' in self.tools:
            result = self.tools['create_file']['function'](filepath, js_content)
        else:
            # Fallback to direct file creation
            try:
                os.makedirs('project-code', exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                result = f"Successfully created {filepath} with LLM-generated content"
            except Exception as e:
                result = f"Error creating JavaScript file: {e}"
                
        print(f"✅ {result}")
        return result
        
    def _create_html_file(self, step: str) -> str:
        """Create an HTML file based on the step description using LLM"""
        print(f"🤖 Using LLM to generate HTML content for: {step}")
        
        # Create a detailed prompt for the LLM
        prompt = f"""
You are an expert web developer. Create a complete, modern HTML file based on this requirement:

"{step}"

Requirements:
- Create a complete, valid HTML5 document
- Include proper meta tags and document structure
- Make it visually appealing with modern styling
- Ensure it's responsive and accessible
- Include relevant content based on the step description

Please provide ONLY the HTML code, no explanations or additional text.
"""
        
        # Get HTML content from LLM
        html_content = self._call_llm(prompt)
        
        if not html_content:
            return "Error: Failed to generate HTML content with LLM"
        
        # Extract code if it's wrapped in code blocks
        html_content = self._extract_code_from_llm_response(html_content)
        
        # Use the file creation tool
        if 'create_file' in self.tools:
            result = self.tools['create_file']['function']('project-code/index.html', html_content)
        else:
            # Fallback to direct file creation
            try:
                os.makedirs('project-code', exist_ok=True)
                with open('project-code/index.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                result = "Successfully created project-code/index.html with LLM-generated content"
            except Exception as e:
                result = f"Error creating HTML file: {e}"
                
        print(f"✅ {result}")
        return result
        
    def _add_styling(self, step: str) -> str:
        """Add styling to the HTML file using LLM"""
        html_file = 'project-code/index.html'
        
        if not os.path.exists(html_file):
            return "Error: HTML file not found. Create it first."
            
        try:
            # Read current file
            with open(html_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            print(f"🤖 Using LLM to generate CSS styling for: {step}")
            
            # Create a detailed prompt for the LLM
            prompt = f"""
You are an expert web developer and designer. I have an existing HTML file and need to add beautiful, modern styling based on this requirement:

"{step}"

Current HTML content:
{current_content}

Requirements:
- Add modern, responsive CSS styling
- Make it visually appealing with good design principles
- Ensure accessibility and usability
- Use modern CSS features (flexbox, grid, animations if appropriate)
- Make it mobile-responsive
- Follow the styling requirement in the step description

Please provide the COMPLETE updated HTML file with the CSS styling included (either in <style> tags or as a separate CSS file if you also provide that). Provide ONLY the code, no explanations.
"""
            
            # Get styled content from LLM
            styled_content = self._call_llm(prompt)
            
            if not styled_content:
                return "Error: Failed to generate styled content with LLM"
            
            # Extract code if it's wrapped in code blocks
            styled_content = self._extract_code_from_llm_response(styled_content)
            
            # Write the updated content back to the file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(styled_content)
                
            result = "Successfully added LLM-generated styling to index.html"
            
        except Exception as e:
            result = f"Error adding styling: {e}"
            
        print(f"✅ {result}")
        return result
        
    def _execute_general_step(self, step: str) -> str:
        """Execute a general step using LLM reasoning"""
        print(f"🤖 Using LLM to execute general step: {step}")
        
        # Create a detailed prompt for the LLM
        prompt = f"""
You are an expert software developer. I need help executing this development step:

"{step}"

Context: This is part of a larger software project. Please analyze what needs to be done and provide specific instructions or code to accomplish this step.

If this step requires creating files, modifying code, or implementing functionality, please provide:
1. A clear explanation of what needs to be done
2. Any code that should be created or modified
3. File names and structure if applicable

Focus on practical implementation details.
"""
        
        # Get instructions from LLM
        llm_response = self._call_llm(prompt)
        
        if not llm_response:
            return f"Error: Failed to get LLM guidance for step: {step}"
        
        # Check if the LLM response contains code that should be saved to files
        if "```" in llm_response and ("create" in step.lower() or "file" in step.lower()):
            # Try to extract and save any code files mentioned
            try:
                self._process_llm_file_instructions(llm_response, step)
            except Exception as e:
                print(f"Warning: Could not process file instructions: {e}")
        
        result = f"LLM executed step successfully. Response: {llm_response[:200]}..."
        print(f"✅ {result}")
        return result
    
    def _process_llm_file_instructions(self, llm_response: str, step: str):
        """Process LLM response to extract and create any files mentioned"""
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', llm_response, re.DOTALL)
        
        # Look for file names in the response
        filename_patterns = [
            r'create\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?["`]?([^\s"`]+\.\w+)["`]?',
            r'save\s+(?:this\s+)?(?:as\s+)?["`]?([^\s"`]+\.\w+)["`]?',
            r'filename:\s*["`]?([^\s"`]+\.\w+)["`]?',
            r'file:\s*["`]?([^\s"`]+\.\w+)["`]?'
        ]
        
        filenames = []
        for pattern in filename_patterns:
            matches = re.findall(pattern, llm_response, re.IGNORECASE)
            filenames.extend(matches)
        
        # Create files if we found both code blocks and filenames
        if code_blocks and filenames:
            os.makedirs('project-code', exist_ok=True)
            
            for i, (lang, code) in enumerate(code_blocks):
                if i < len(filenames):
                    filename = filenames[i]
                    filepath = os.path.join('project-code', filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(code.strip())
                    
                    print(f"📁 Created file: {filepath}")
                elif len(code_blocks) == 1 and len(filenames) >= 1:
                    # If there's one code block and one or more filenames, use the first filename
                    filename = filenames[0]
                    filepath = os.path.join('project-code', filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(code.strip())
                    
                    print(f"📁 Created file: {filepath}")
        
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
