# AutoGen Coding Agent

> **🎉 NEW: Fully LLM-Driven Implementation!**  
> This agent now uses **Language Models** (LM Studio, OpenAI, etc.) to generate all code dynamically instead of hardcoded templates. See `LLM_INTEGRATION_README.md` for detailed documentation.

A **fully LLM-driven** AI coding agent that generates code dynamically using Language Models instead of hardcoded templates.

## 🚀 Key Features

✅ **LLM-Driven Code Generation**: All code is generated through AI reasoning, not templates  
✅ **Streamlit UI**: User-friendly interface with real-time progress and file preview  
✅ **Multi-Provider Support**: LM Studio (local), OpenAI, Anthropic, Groq  
✅ **Intelligent Task Execution**: Automatically determines file types and implementation approach  
✅ **Dynamic Content Creation**: Adapts to any project type or programming language  
✅ **RAG Integration**: Understands and reasons over existing codebases  

## 🎯 What Makes This Different

### Before (Template-Based)
- Hardcoded HTML/CSS/JS templates
- Limited to predefined project types
- Static, unchanging output
- Manual template maintenance

### After (LLM-Driven)
- AI generates all code based on requirements
- Supports any programming language or framework
- Dynamic, contextual output
- Self-improving through LLM updates

## 📁 Project Structure

```plaintext
autogen-coding-agent/
├── agent/
│   ├── utils/                 ← Core utility modules
│   │   ├── __init__.py
│   │   ├── config.py          ← Configuration management
│   │   ├── file_ops.py        ← File operations
│   │   ├── code_embedding.py  ← RAG functionality
│   │   └── agents.py          ← Agent creation
│   ├── extensions/            ← Extension modules
│   │   ├── __init__.py
│   │   └── git_integration.py ← Git functionality
│   ├── code_agent.py          ← Main agent logic
│   ├── config.yaml            ← Configuration file
│   └── tasks.md               ← Developer-style task list
├── project-code/              ← Your target repo or codebase
│   └── game.js                ← Example JS file
├── requirements.txt
├── test_modules.py            ← Module testing script
├── run_agent.py               ← Simple runner
└── README.md
```

## 🏃 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

Edit the `.env` file and replace `your-key-here` with your actual OpenAI API key.

### 3. Run the agent

```bash
python agent/code_agent.py
```

## 🧠 How It Works

1. The agent first embeds your codebase using LangChain and FAISS vector storage
2. When run, it queries for relevant code based on your tasks
3. The AutoGen assistant agent analyzes the code and tasks
4. It proposes code changes to solve the tasks

## 🏗️ Modular Architecture

The agent is built with a modular architecture that makes it easy to extend:

### Core Modules
- **`utils/config.py`** - Configuration loading with YAML support
- **`utils/file_ops.py`** - File reading, writing, and diff operations
- **`utils/code_embedding.py`** - RAG functionality using LangChain
- **`utils/agents.py`** - AutoGen agent creation and management

### Extensions System
- **`extensions/`** - Plugin-style extensions
- **`extensions/git_integration.py`** - Git operations (init, add, commit, status)
- Extensions can be enabled/disabled via `config.yaml`

### Adding New Features
1. Create a new module in `utils/` for core features
2. Create extension modules in `extensions/` for optional features
3. Register extensions in `extensions/__init__.py`
4. Enable in `config.yaml`

## 🧠 Extending This Project

You can extend this agent with:

* ✅ File writing (apply edits via diffs)
* ✅ Git commands (auto commit)
* ✅ Local LLMs via LangChain + Ollama
* ✅ UI via Gradio or Streamlit

## Customization

1. Edit `tasks.md` to specify what you want the agent to work on
2. Modify `config.yaml` to adjust agent parameters
3. Extend `code_agent.py` with additional capabilities like file writing

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in requirements.txt

## 🎯 MCP-Style Loader (New!)

We've added an MCP (Model Context Protocol) style loader that directly executes tasks without the complexity of AutoGen function calls.

### Quick Start with MCP Loader

```bash
# Run the MCP loader (recommended)
python run_mcp_loader.py

# Or run the test
python test_mcp_loader.py
```

**Why MCP Loader?**
- ✅ **Reliable Execution** - No function call interpretation issues
- ✅ **Direct File Creation** - Actually creates and modifies files
- ✅ **Beautiful Results** - Generates styled HTML with animations
- ✅ **Clear Feedback** - Step-by-step execution reporting

### MCP vs AutoGen Approach

| Feature | AutoGen Approach | MCP Loader Approach |
|---------|------------------|---------------------|
| Function Calls | ❌ Execution issues | ✅ Direct execution |
| File Creation | ❌ Suggestions only | ✅ Actually creates files |
| Reliability | ⚠️ Inconsistent | ✅ Guaranteed results |
| Complexity | 🔴 High | 🟢 Simple |
