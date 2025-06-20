"""
Quick Setup and Test Script for AutoGen Coding Agent

This script verifies that the AutoGen Coding Agent is properly set up
and ready to run.
"""

import os
import sys
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def print_result(test_name, success, details=""):
    """Print test result with emoji"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_environment():
    """Test environment setup"""
    print_header("TESTING ENVIRONMENT SETUP")
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print_result("Python Version", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_result("Python Version", False, f"Python {python_version.major}.{python_version.minor} (requires 3.8+)")
        return False
    
    # Test environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print_result("OpenAI API Key", False, "OPENAI_API_KEY not found in .env file")
        return False
    elif api_key == "your-key-here":
        print_result("OpenAI API Key", False, "Please replace 'your-key-here' with your actual OpenAI API key")
        return False
    else:
        # Mask the key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print_result("OpenAI API Key", True, f"Found: {masked_key}")
    
    return True

def test_dependencies():
    """Test that all required dependencies are installed"""
    print_header("TESTING DEPENDENCIES")
    
    dependencies = {
        "openai": "OpenAI API client",
        "langchain": "LangChain framework",
        "langchain_community": "LangChain community extensions",
        "autogen": "AutoGen framework", 
        "tiktoken": "Token counting",
        "faiss": "Vector similarity search",
        "yaml": "YAML parsing",
        "dotenv": "Environment variables"
    }
    
    all_good = True
    for module, description in dependencies.items():
        try:
            if module == "autogen":
                import autogen
            elif module == "dotenv":
                import dotenv
            elif module == "yaml":
                import yaml
            else:
                __import__(module)
            print_result(description, True)
        except ImportError as e:
            print_result(description, False, f"Import error: {e}")
            all_good = False
    
    return all_good

def test_project_structure():
    """Test that all required files and directories exist"""
    print_header("TESTING PROJECT STRUCTURE")
    
    required_files = [
        ("agent/code_agent.py", "Main agent file"),
        ("agent/config.yaml", "Configuration file"),
        ("agent/tasks.md", "Tasks file"),
        ("agent/utils/__init__.py", "Utils package"),
        ("agent/utils/config.py", "Config module"),
        ("agent/utils/file_ops.py", "File operations module"),
        ("agent/utils/code_embedding.py", "Code embedding module"),
        ("agent/utils/agents.py", "Agent utilities module"),
        ("agent/extensions/__init__.py", "Extensions package"),
        ("agent/extensions/git_integration.py", "Git integration"),
        ("project-code/game.js", "Example code file"),
        ("requirements.txt", "Dependencies file"),
        ("README.md", "Documentation"),
        (".env", "Environment variables")
    ]
    
    all_good = True
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print_result(description, True, file_path)
        else:
            print_result(description, False, f"Missing: {file_path}")
            all_good = False
    
    return all_good

def test_module_imports():
    """Test that our modules can be imported successfully"""
    print_header("TESTING MODULE IMPORTS")
    
    all_good = True
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    modules_to_test = [
        ("agent.utils.config", "Configuration utilities"),
        ("agent.utils.file_ops", "File operation utilities"),
        ("agent.utils.code_embedding", "Code embedding utilities"),
        ("agent.utils.agents", "Agent utilities"),
        ("agent.extensions.git_integration", "Git integration extension")
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_result(description, True)
        except ImportError as e:
            print_result(description, False, f"Import error: {e}")
            all_good = False
    
    return all_good

def test_configuration():
    """Test configuration loading"""
    print_header("TESTING CONFIGURATION")
    
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from agent.utils.config import load_config
        config = load_config()
        
        required_sections = ['llm', 'rag', 'agent', 'extensions']
        all_good = True
        
        for section in required_sections:
            if section in config:
                print_result(f"Config section: {section}", True)
            else:
                print_result(f"Config section: {section}", False, "Missing section")
                all_good = False
        
        # Test specific config values
        llm_model = config.get('llm', {}).get('model', 'unknown')
        print_result("LLM Model Configuration", True, f"Using {llm_model}")
        
        return all_good
        
    except Exception as e:
        print_result("Configuration Loading", False, f"Error: {e}")
        return False

def test_file_operations():
    """Test basic file operations"""
    print_header("TESTING FILE OPERATIONS")
    
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from agent.utils.file_ops import read_file, load_tasks
        
        # Test reading README
        readme_content = read_file("README.md")
        if "AutoGen Coding Agent" in readme_content:
            print_result("File Reading", True, "Successfully read README.md")
        else:
            print_result("File Reading", False, "Could not read README.md properly")
            return False
        
        # Test loading tasks
        tasks_content = load_tasks()
        if "Task" in tasks_content or "task" in tasks_content.lower():
            print_result("Task Loading", True, "Successfully loaded tasks.md")
        else:
            print_result("Task Loading", False, "Could not load tasks.md properly")
            return False
        
        return True
        
    except Exception as e:
        print_result("File Operations", False, f"Error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print_header("🚀 AutoGen Coding Agent - Setup Verification")
    
    tests = [
        ("Environment Setup", test_environment),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_module_imports),
        ("Configuration", test_configuration),
        ("File Operations", test_file_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(test_name, False, f"Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("📊 SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_result(test_name, result)
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_header("🎉 SUCCESS - Ready to Run!")
        print("Your AutoGen Coding Agent is fully set up and ready to use!")
        print("\nTo run the agent:")
        print("  python agent/code_agent.py")
        print("\nOr use the runner script:")
        print("  python run_agent.py")
        return True
    else:
        print_header("❌ SETUP INCOMPLETE")
        print("Please fix the issues above before running the agent.")
        print("\nFor help, check:")
        print("  - README.md for setup instructions")
        print("  - requirements.txt for dependencies")
        print("  - .env file for API key configuration")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
