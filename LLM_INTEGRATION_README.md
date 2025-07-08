# AutoGen Coding Agent - LLM-Driven Implementation

## Overview

This AutoGen Coding Agent has been completely refactored to use **LLM reasoning** for all code generation instead of hardcoded templates. The agent now leverages Language Models (like LM Studio) to dynamically generate code based on user requirements.

## Key Features

### ✅ Complete LLM Integration
- **No hardcoded templates**: All code generation is now done through LLM calls
- **Dynamic content creation**: Files are generated based on AI reasoning, not pre-written templates
- **Intelligent task interpretation**: The LLM analyzes each task step and determines the best implementation approach

### ✅ Streamlit UI Enhancements
- **LLM Connection Testing**: Built-in connection testing for LM Studio
- **Flexible Task Input**: Support for direct input, file upload, or example tasks
- **Real-time Progress**: Live feedback during code generation
- **File Preview & Download**: View generated files and download as ZIP
- **Configuration Options**: Adjustable temperature, tokens, and advanced settings

### ✅ Agent Architecture
- **MCPLoader**: Enhanced with LLM integration for dynamic task execution
- **Smart File Detection**: Automatically determines file types and generates appropriate content
- **Error Handling**: Robust error handling and fallback mechanisms
- **Tool Registration**: Modular tool system for file operations

## Architecture Changes

### Before (Template-Based)
```python
def create_simple_web_project(project_dir, tasks_content):
    html_content = '''<!DOCTYPE html>
    <html>
        <head><title>Static Template</title></head>
        <body><h1>Hardcoded Content</h1></body>
    </html>'''
    # Write hardcoded template...
```

### After (LLM-Driven)
```python
def _create_html_file(self, step: str) -> str:
    prompt = f"""
    You are an expert web developer. Create a complete, modern HTML file based on this requirement:
    "{step}"
    
    Requirements:
    - Create a complete, valid HTML5 document
    - Include proper meta tags and document structure
    - Make it visually appealing with modern styling
    - Ensure it's responsive and accessible
    """
    
    html_content = self._call_llm(prompt)
    # Process and save LLM-generated content...
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup LM Studio (Recommended)
1. Download and install LM Studio
2. Load a model (e.g., Phi-2, CodeLlama, or similar)
3. Start the server (Server tab → Start)
4. Ensure it's running on `http://localhost:1234`

### 3. Test the Setup
```bash
# Test LLM connection
python test_llm_agent.py

# Or run the Streamlit UI
python run_streamlit_app.py
```

## Usage

### Streamlit UI
```bash
python run_streamlit_app.py
```

1. **Configure LLM**: Select provider, temperature, and other settings
2. **Test Connection**: Use the "Test LLM Connection" button
3. **Define Tasks**: Enter tasks directly, upload a file, or use examples
4. **Execute**: Choose between Standard (in-app) or Direct (subprocess) execution
5. **Review Results**: View generated files, preview HTML, and download outputs

### Direct Agent Usage
```python
from agent.mcp_loader import MCPLoader

config = {
    'llm': {
        'provider': 'lmstudio',
        'temperature': 0.3,
        'max_tokens': 2000
    }
}

loader = MCPLoader("tasks.md", config)
tasks = loader.load_tasks()
results = loader.run_all_tasks()
```

## Task Examples

### Web Application
```markdown
## Task 1: Create HTML Structure
- Create a modern landing page with header, navigation, and hero section
- Include responsive design and accessibility features

## Task 2: Add Interactive Features
- Create JavaScript for smooth scrolling navigation
- Add a contact form with validation
```

### Python Project
```markdown
## Task 1: Create Core Application
- Build a command-line calculator with advanced operations
- Include error handling and input validation

## Task 2: Add Testing
- Create comprehensive unit tests
- Ensure edge case coverage
```

## LLM Integration Details

### Supported Providers
- **LM Studio** (Primary): Local LLM hosting
- **OpenAI** (Planned): GPT models
- **Anthropic** (Planned): Claude models
- **Groq** (Planned): Fast inference

### LLM Functions

#### Core Generation Methods
- `_call_llm(prompt)`: Main LLM communication
- `_create_html_file(step)`: HTML generation
- `_add_styling(step)`: CSS styling
- `_create_javascript_with_llm(step)`: JavaScript functionality
- `_create_file_with_llm(step)`: General file creation
- `_execute_general_step(step)`: Generic task execution

#### Content Processing
- `_extract_code_from_llm_response()`: Extract code blocks
- `_process_llm_file_instructions()`: Parse file creation instructions

## Files Modified

### Core Agent Files
- `agent/mcp_loader.py`: Complete LLM integration
- `streamlit_app.py`: Enhanced UI with LLM features
- `test_llm_agent.py`: Test harness for LLM functionality

### Utility Files (Enhanced)
- `agent/utils/llm_client.py`: LLM communication
- `agent/utils/file_ops.py`: File operations
- `agent/utils/config.py`: Configuration management

## Benefits of LLM-Driven Approach

### ✅ Dynamic Content Generation
- Content adapts to specific requirements
- No limitations of pre-written templates
- Intelligent interpretation of user intent

### ✅ Improved Code Quality
- Modern coding practices from LLM training
- Proper structure and documentation
- Best practices automatically applied

### ✅ Flexibility
- Supports any programming language
- Adapts to different project types
- Handles complex, multi-step requirements

### ✅ Scalability
- Easy to add new project types
- No need to write new templates
- Self-improving through LLM updates

## Troubleshooting

### LM Studio Connection Issues
1. Ensure LM Studio is running
2. Check server is enabled on port 1234
3. Verify a model is loaded
4. Test with: `curl http://localhost:1234/v1/models`

### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Test imports
python -c "from agent.mcp_loader import MCPLoader; print('Success')"
```

### Generated Code Issues
- Increase max_tokens for complex projects
- Adjust temperature for creativity vs. consistency
- Review LLM prompts for clarity

## Future Enhancements

- [ ] Support for additional LLM providers
- [ ] Enhanced prompt engineering
- [ ] Code review and optimization features
- [ ] Integration with version control
- [ ] Multi-agent collaboration
- [ ] Project templates from successful generations

## Contributing

When contributing to this project, ensure that:
1. No hardcoded templates are added
2. All content generation goes through LLM calls
3. Proper error handling is maintained
4. Tests are updated for new features

---

**Made with ❤️ and 🤖 by Your AutoGen Coding Agent**
