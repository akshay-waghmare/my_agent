"""
Streamlit UI for AutoGen Coding Agent

This app provides a user-friendly interface to interact with the
AutoGen Coding Agent, allowing users to specify tasks, project types,
and view the generated code and execution results.
"""

import os
import sys
import streamlit as st
import yaml
from pathlib import Path
import tempfile
import shutil
import time
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import agent utilities with error handling
try:
    from agent.utils.config import load_config
    from agent.utils.file_ops import read_file, create_file, write_file
    from agent.mcp_loader import MCPLoader
    CONFIG_AVAILABLE = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Some features may not be available. Please check your dependencies.")
    CONFIG_AVAILABLE = False
    
    # Fallback functions
    def load_config():
        return {
            "llm": {"provider": "lmstudio", "temperature": 0.2, "max_tokens": 2000},
            "rag": {"embeddings_provider": "local", "similarity_top_k": 3},
            "agent": {"verbose": True}
        }
    
    def read_file(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def create_file(path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def write_file(path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

try:
    from agent.utils.llm_client import LLMClient
    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False
import subprocess
import json

# Set page configuration
st.set_page_config(
    page_title="AutoGen Coding Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the app's appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2196F3;
        margin-top: 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .file-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .output-box {
        background-color: #f0f0f0;
        border-left: 3px solid #2196F3;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        overflow: auto;
        max-height: 400px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function for the Streamlit app"""
    
    # Show import status
    if not CONFIG_AVAILABLE:
        st.warning("⚠️ Some agent features are not available due to import issues. Running in simplified mode.")
    
    # Header
    st.markdown("<h1 class='main-header'>🤖 AutoGen Coding Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your AI-powered coding assistant</p>", unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Project Type
        project_type = st.selectbox(
            "Project Type",
            ["web", "python", "javascript", "java", "game", "generic"],
            index=0
        )
        
        # LLM Provider
        providers = ["lmstudio", "openai", "groq", "anthropic"]
        provider = st.selectbox("LLM Provider", providers, index=0)
        
        # Test LLM Connection
        if st.button("Test LLM Connection"):
            with st.spinner("Testing LLM connection..."):
                try:
                    if provider == "lmstudio":
                        # Test local LM Studio connection - first check server status
                        import requests
                        
                        try:
                            # First check if server is reachable with a simple request
                            server_check = requests.get("http://localhost:1234/", timeout=2)
                            st.info("LM Studio server is reachable. Testing model...")
                        except:
                            st.error("❌ LM Studio server not found at http://localhost:1234/")
                            st.info("Make sure LM Studio is running with the server enabled (Server tab → Start)")
                            return
                        
                        # Now try a simple completion with a longer timeout
                        response = requests.post(
                            "http://localhost:1234/v1/chat/completions",
                            headers={"Content-Type": "application/json"},
                            json={
                                "model": "default",
                                "messages": [{"role": "user", "content": "Say hello"}],
                                "max_tokens": 20  # Limit tokens to make it faster
                            },
                            timeout=30  # Increased timeout
                        )
                        if response.status_code == 200:
                            model_name = response.json().get("model", "unknown")
                            st.success(f"✅ Connected to LM Studio! Model: {model_name}")
                        else:
                            st.error(f"❌ Failed to connect to LM Studio: {response.status_code} {response.text}")
                    else:
                        # For other providers, we'd check API keys
                        api_key = os.getenv(f"{provider.upper()}_API_KEY", "")
                        if not api_key:
                            st.error(f"❌ No API key found for {provider.upper()}. Please add it to your .env file.")
                        else:
                            st.success(f"✅ {provider.upper()} API key found. Ready to connect.")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
                    st.info("Make sure LM Studio is running with the server enabled on port 1234.")
                    
                    # Show troubleshooting tips
                    with st.expander("Troubleshooting Tips"):
                        st.markdown("""
                        ### Troubleshooting LM Studio Connection
                        
                        1. **Check LM Studio is running** - Open LM Studio application
                        2. **Enable the server** - Go to Server tab and click "Start"
                        3. **Verify port** - Make sure it's running on port 1234 (default)
                        4. **Load a model** - Make sure you've loaded a model (like Phi-2)
                        5. **Check firewall** - Ensure your firewall isn't blocking connections
                        6. **Restart LM Studio** - Sometimes restarting helps
                        
                        **Testing Connection Manually:**
                        ```powershell
                        Invoke-RestMethod -Uri "http://localhost:1234/v1/chat/completions" `
                          -Method Post `
                          -ContentType "application/json" `
                          -Body '{"model": "default", "messages": [{"role": "user", "content": "hi"}]}'
                        ```
                        """)
                    
        
        # Temperature
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        
        # Advanced Settings Expander
        with st.expander("Advanced Settings"):
            max_tokens = st.slider("Max Tokens", min_value=500, max_value=8000, value=2000, step=500)
            multi_agent = st.checkbox("Use Multi-Agent System", value=True)
            verbose = st.checkbox("Verbose Output", value=True)
            
            # RAG Settings
            st.subheader("RAG Settings")
            embedding_provider = st.selectbox(
                "Embeddings Provider",
                ["local", "openai", "code"],
                index=0
            )
            
            similarity_top_k = st.slider("Top K Results", min_value=1, max_value=10, value=3)
    
    # Add option to run with direct subprocess for better output
    run_method = st.radio(
        "Run Method",
        ["Standard (In-App)", "Direct (Subprocess)"],
        index=0,
        help="Standard runs the agent inside the app. Direct runs it as a subprocess which may provide better output."
    )
    
    # Main content area
    st.header("Task Definition")
    
    # Task Input
    task_input_method = st.radio(
        "How would you like to define tasks?",
        ["Direct Input", "Upload tasks.md", "Use Example"]
    )
    
    tasks_content = ""
    
    if task_input_method == "Direct Input":
        tasks_content = st.text_area(
            "Enter your tasks here",
            """# Coding Tasks

## Task 1: Create a Hello World
- Create a simple Hello World application

## Task 2: Add Styling
- Add some basic styling to make it look nice
""",
            height=200
        )
    
    elif task_input_method == "Upload tasks.md":
        uploaded_file = st.file_uploader("Upload tasks.md file", type=["md"])
        if uploaded_file is not None:
            tasks_content = uploaded_file.getvalue().decode("utf-8")
            st.success("File uploaded successfully!")
    
    else:  # Use Example
        example_task = st.selectbox(
            "Choose an example task",
            ["Simple Web App", "Python Calculator", "Bubble Shooter Game"]
        )
        
        if example_task == "Simple Web App":
            tasks_content = """# Web Application Tasks

## Task 1: Create HTML Structure
- Create a basic HTML file with proper structure
- Add a header, main content area, and footer
- Include a navigation menu

## Task 2: Add CSS Styling
- Create a CSS file with responsive design
- Style the header, navigation, content, and footer
- Ensure it works on mobile devices

## Task 3: Add JavaScript Functionality
- Create a script.js file
- Add a dark mode toggle button
- Implement form validation
"""
        elif example_task == "Python Calculator":
            tasks_content = """# Python Calculator Tasks

## Task 1: Create Basic Calculator
- Create a Python script for basic arithmetic operations
- Implement addition, subtraction, multiplication, division
- Add input validation

## Task 2: Add Advanced Features
- Add support for square root, power, and modulo
- Implement memory functions (store, recall, clear)
- Add a command-line interface

## Task 3: Add Unit Tests
- Create test cases for all calculator functions
- Test edge cases and error handling
- Ensure 100% code coverage
"""
        else:  # Bubble Shooter Game
            tasks_content = """# Bubble Shooter Game Tasks

## Task 1: Create Game Structure
- Set up HTML5 canvas
- Create basic game layout
- Implement game initialization

## Task 2: Implement Core Mechanics
- Add bubble creation and colors
- Implement shooting mechanism
- Add collision detection

## Task 3: Add Game Logic
- Implement scoring system
- Add level progression
- Create win/lose conditions

## Task 4: Polish and Finalize
- Add sounds and visual effects
- Implement high score system
- Make the game responsive
"""
    
    # Show the final task content
    if tasks_content:
        with st.expander("View Tasks Content", expanded=False):
            st.markdown(tasks_content)
    
    # Project Directory
    st.subheader("Project Directory")
    project_dir = st.text_input("Project Directory", "project-code")
    
    # Execute Button
    execute_col1, execute_col2 = st.columns([1, 5])
    with execute_col1:
        if run_method == "Standard (In-App)":
            execute_button = st.button("Execute Tasks", type="primary")
        else:
            execute_button = st.button("Run Agent (Direct)", type="primary")
    with execute_col2:
        if execute_button:
            st.info("Task execution started. Please wait...")
    
    # Direct subprocess execution
    if run_method == "Direct (Subprocess)" and execute_button and tasks_content:
        st.header("Agent Execution")
        
        # Save tasks to a temporary file
        temp_dir = tempfile.mkdtemp()
        tasks_file_path = os.path.join(temp_dir, "tasks.md")
        
        with open(tasks_file_path, "w") as f:
            f.write(tasks_content)
        
        # Create project directory if it doesn't exist
        os.makedirs(project_dir, exist_ok=True)
        
        # Display running status
        st.info("Starting agent subprocess...")
        
        # Create output area
        output_area = st.empty()
        
        try:
            # Run the agent as a subprocess
            process, _ = run_agent_subprocess(
                tasks_file_path,
                project_dir,
                project_type,
                provider,
                temperature,
                max_tokens,
                multi_agent,
                verbose
            )
            
            # Display real-time output
            output_text = ""
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_text += line
                    output_area.code(output_text)
            
            # Show completion status
            if process.returncode == 0:
                st.success("Agent completed successfully!")
            else:
                st.error(f"Agent exited with code {process.returncode}")
            
            # Show created files
            if os.path.exists(project_dir):
                files = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
                
                if files:
                    st.subheader("Created Files")
                    
                    for file in files:
                        file_path = os.path.join(project_dir, file)
                        file_size = os.path.getsize(file_path)
                        
                        with st.expander(f"{file} ({file_size} bytes)"):
                            try:
                                content = read_file(file_path)
                                
                                # Determine if it's code and needs syntax highlighting
                                extension = os.path.splitext(file)[1].lower()
                                if extension in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.ts']:
                                    st.code(content, language=extension[1:])
                                else:
                                    st.text(content)
                                
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
            
        except Exception as e:
            st.error(f"Error running agent: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            
        finally:
            # Clean up
            try:
                os.unlink(tasks_file_path)
                os.rmdir(temp_dir)
            except:
                pass
    
    # Standard in-app execution
    elif run_method == "Standard (In-App)" and execute_button and tasks_content:
        # Create a temporary tasks.md file
        temp_dir = tempfile.mkdtemp()
        tasks_file_path = os.path.join(temp_dir, "tasks.md")
        
        with open(tasks_file_path, "w") as f:
            f.write(tasks_content)
        
        # Update configuration
        config = load_config()
        config["llm"] = {
            "provider": provider,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        config["rag"]["embeddings_provider"] = embedding_provider
        config["rag"]["similarity_top_k"] = similarity_top_k
        config["agent"]["verbose"] = verbose
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute tasks
        try:
            status_text.text("Initializing agent...")
            progress_bar.progress(10)
            
            if CONFIG_AVAILABLE:
                # Initialize MCPLoader
                loader = MCPLoader(tasks_file_path)
                loader.register_tool("create_file", create_file, "Create a new file")
                loader.register_tool("write_file", write_file, "Write content to a file")
                loader.register_tool("read_file", read_file, "Read content from a file")
                
                status_text.text("Loading tasks...")
                progress_bar.progress(20)
                
                # Load tasks
                tasks = loader.load_tasks()
                
                if not tasks:
                    st.error("❌ No tasks found. Please check your tasks file.")
                    return
                
                # Update progress
                status_text.text(f"Found {len(tasks)} tasks to execute...")
                progress_bar.progress(30)
                
                # Execute all tasks
                results = loader.run_all_tasks()
                
                # Show summary
                status_text.text("Generating summary...")
                progress_bar.progress(90)
                
                summary = loader.get_summary(results)
                
            else:
                # Fallback: Use LLM directly to generate code
                status_text.text("Running with direct LLM integration...")
                progress_bar.progress(30)
                
                # Create project directory
                os.makedirs(project_dir, exist_ok=True)
                
                # Use LLM to generate project files
                if provider == "lmstudio":
                    generate_project_with_llm(project_dir, project_type, tasks_content, provider, temperature, max_tokens)
                else:
                    st.error("❌ Direct LLM integration only supports LM Studio currently. Please fix import issues or use LM Studio.")
                    return
                
                progress_bar.progress(80)
                summary = "Tasks executed using direct LLM integration. Files generated based on AI reasoning."
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Task execution completed!")
            
            # Show results
            st.subheader("Execution Results")
            st.markdown(f"<div class='output-box'>{summary}</div>", unsafe_allow_html=True)
            
            # Show created files
            if os.path.exists(project_dir):
                files = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
                
                if files:
                    st.subheader("Created Files")
                    
                    for file in files:
                        file_path = os.path.join(project_dir, file)
                        file_size = os.path.getsize(file_path)
                        
                        with st.expander(f"{file} ({file_size} bytes)"):
                            try:
                                content = read_file(file_path)
                                
                                # Determine if it's code and needs syntax highlighting
                                extension = os.path.splitext(file)[1].lower()
                                if extension in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.ts']:
                                    st.code(content, language=extension[1:])
                                else:
                                    st.text(content)
                                
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
                
                # Add interactive features for working with generated files
                if any(file.endswith('.html') for file in files):
                    html_file = next(file for file in files if file.endswith('.html'))
                    html_path = os.path.join(project_dir, html_file)
                    
                    # Preview HTML directly in the app
                    with st.expander("Preview HTML Result", expanded=True):
                        html_content = read_file(html_path)
                        st.components.v1.html(html_content, height=500)
                    
                    # Option to download the file
                    with open(html_path, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="Download HTML file",
                            data=f.read(),
                            file_name=html_file,
                            mime="text/html",
                        )
                
                # Add option to download all files as a zip
                if files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                        temp_zip_path = tmp.name
                    
                    shutil.make_archive(
                        temp_zip_path.replace('.zip', ''), 
                        'zip', 
                        project_dir
                    )
                    
                    with open(temp_zip_path, "rb") as f:
                        st.download_button(
                            label="Download All Files (ZIP)",
                            data=f,
                            file_name="project_files.zip",
                            mime="application/zip",
                        )
            
        except Exception as e:
            st.error(f"Error executing tasks: {str(e)}")
            import traceback
            st.code(traceback.format_exc(), language="python")
        
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ by Your AutoGen Coding Agent")

def run_agent_subprocess(tasks_file_path, project_dir, project_type, provider, temperature, 
                 max_tokens, multi_agent, verbose):
    """Run the agent as a subprocess to get real-time output"""
    
    cmd = [
        "python", "run_project_agent.py",
        "--project-dir", project_dir,
        "--tasks-file", tasks_file_path,
        "--project-type", project_type
    ]
    
    if multi_agent:
        cmd.append("--multi-agent")
    
    if verbose:
        cmd.append("--verbose")
    
    # Create a temporary config file with the LLM settings
    config = {
        "llm": {
            "provider": provider,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }
    
    temp_config_path = os.path.join(tempfile.gettempdir(), "temp_agent_config.yaml")
    with open(temp_config_path, "w") as f:
        yaml.dump(config, f)
    
    cmd.extend(["--config", temp_config_path])
    
    # Run the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    output = []
    
    # Return the process to be monitored by the caller
    return process, output

def generate_project_with_llm(project_dir, project_type, tasks_content, provider, temperature, max_tokens):
    """Generate project files using direct LLM calls"""
    import requests
    import json
    import re
    
    def call_llm(prompt):
        """Call LM Studio API directly"""
        try:
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                st.error(f"LLM API error: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Error calling LLM: {str(e)}")
            return None
    
    def extract_code_blocks(text):
        """Extract code blocks from LLM response"""
        # Pattern to match code blocks with language specification
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def extract_filename_and_content(text):
        """Extract filename and content from LLM response"""
        # Look for patterns like "filename: file.ext" or "File: file.ext"
        filename_pattern = r'(?:filename|file|create|save)\s*[:\-]\s*([^\n]+)'
        filename_match = re.search(filename_pattern, text, re.IGNORECASE)
        
        if filename_match:
            filename = filename_match.group(1).strip()
            # Clean up filename
            filename = re.sub(r'[^\w\.-]', '', filename)
            return filename
        return None
    
    # Step 1: Plan the project structure
    planning_prompt = f"""
You are an expert software developer. Based on the following task requirements, create a detailed plan for a {project_type} project.

Tasks:
{tasks_content}

Please provide:
1. A list of files that need to be created
2. A brief description of what each file should contain
3. The order in which files should be implemented

Respond in a clear, structured format.
"""
    
    st.info("🤖 Planning project structure...")
    plan = call_llm(planning_prompt)
    
    if not plan:
        st.error("Failed to generate project plan")
        return
    
    # Show the plan to the user
    with st.expander("📋 Project Plan", expanded=True):
        st.markdown(plan)
    
    # Step 2: Generate each file based on the plan
    file_generation_prompt = f"""
Based on this project plan and requirements, generate the complete source code files for a {project_type} project.

Project Plan:
{plan}

Original Tasks:
{tasks_content}

Please generate ALL the necessary files with complete, working code. For each file:
1. Clearly indicate the filename
2. Provide the complete code content
3. Ensure the code is production-ready and follows best practices

Format your response as:
filename: [filename]
```[language]
[complete code content]
```

Generate multiple files if needed. Make sure all files work together as a complete project.
"""
    
    st.info("🤖 Generating project files...")
    files_response = call_llm(file_generation_prompt)
    
    if not files_response:
        st.error("Failed to generate project files")
        return
    
    # Parse and create files
    try:
        os.makedirs(project_dir, exist_ok=True)
        
        # Extract all filename patterns and code blocks
        filename_matches = re.findall(r'filename:\s*([^\n]+)', files_response, re.IGNORECASE)
        code_blocks = extract_code_blocks(files_response)
        
        created_files = []
        
        if filename_matches and code_blocks:
            # Match filenames with code blocks
            for i, (lang, code) in enumerate(code_blocks):
                if i < len(filename_matches):
                    filename = filename_matches[i].strip()
                    # Clean filename
                    filename = re.sub(r'[^\w\.-]', '', filename)
                    
                    if filename:
                        filepath = os.path.join(project_dir, filename)
                        create_file(filepath, code.strip())
                        created_files.append(filename)
                        st.success(f"📁 Created: {filename}")
        
        # If no clear filename/code pairs, try to extract files differently
        if not created_files:
            # Look for any file patterns in the response
            file_sections = re.split(r'(?:filename|file):\s*([^\n]+)', files_response, flags=re.IGNORECASE)
            
            for i in range(1, len(file_sections), 2):
                if i + 1 < len(file_sections):
                    filename = file_sections[i].strip()
                    content = file_sections[i + 1].strip()
                    
                    # Extract code if wrapped in code blocks
                    code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
                    if code_match:
                        content = code_match.group(1)
                    
                    if filename and content:
                        filename = re.sub(r'[^\w\.-]', '', filename)
                        filepath = os.path.join(project_dir, filename)
                        create_file(filepath, content.strip())
                        created_files.append(filename)
                        st.success(f"📁 Created: {filename}")
        
        # If still no files, create a default file with the response
        if not created_files:
            default_filename = f"generated_project.{'html' if project_type == 'web' else 'py'}"
            filepath = os.path.join(project_dir, default_filename)
            create_file(filepath, files_response)
            created_files.append(default_filename)
            st.info(f"📁 Created default file: {default_filename}")
        
        # Generate a README
        readme_prompt = f"""
Create a README.md file for this {project_type} project.

Project Files: {', '.join(created_files)}
Original Tasks: {tasks_content}

Include:
- Project description
- How to run/use the project
- File structure explanation
- Any dependencies or setup instructions

Make it professional and helpful.
"""
        
        st.info("📝 Generating README...")
        readme_content = call_llm(readme_prompt)
        
        if readme_content:
            readme_path = os.path.join(project_dir, "README.md")
            create_file(readme_path, readme_content)
            st.success("📁 Created: README.md")
        
        st.success(f"🎉 Project generation completed! Created {len(created_files) + (1 if readme_content else 0)} files.")
        
    except Exception as e:
        st.error(f"Error creating project files: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Run the main function
if __name__ == "__main__":
    main()