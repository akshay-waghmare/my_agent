# Bubble Shooter Game Agent - Streamlit UI

This Streamlit application provides a web-based interface for running the Bubble Shooter Game Agent with Groq AI.

## Features

- **Task Management**: Select and run specific tasks for the Bubble Shooter game development
- **Real-time Monitoring**: View project status, files, and recent activity
- **Configuration**: Easy model selection and project directory management  
- **Testing**: Built-in test runner for agent functionality
- **File Management**: Browse and track generated files

## Getting Started

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Groq API Key**: Set your `GROQ_API_KEY` environment variable
3. **Dependencies**: Install required packages (done automatically)

### Running the UI

#### Option 1: Direct Command
```bash
streamlit run streamlit_app.py
```

#### Option 2: Batch File (Windows)
```bash
run_streamlit_ui.bat
```

#### Option 3: PowerShell Script
```powershell
./run_streamlit_ui.ps1
```

The app will start on `http://localhost:8501`

## Using the Interface

### Main Features

1. **Task Selection**
   - Choose from available Bubble Shooter game tasks
   - View detailed task requirements
   - Add custom context or instructions

2. **Configuration Sidebar**
   - Check API key status
   - Select AI model (Groq options)
   - Set project directory

3. **Project Status Panel**
   - View project files and sizes
   - Check recent file modifications
   - Monitor test status

4. **Quick Actions**
   - Open project directory
   - Run test suites
   - Clean temporary files

### Running a Task

1. Select a task from the dropdown menu
2. Review the task requirements displayed
3. Optionally add custom context in the text area
4. Click "🚀 Run Task X" to execute
5. Monitor progress and results in real-time

### Available Tasks

- **Task 1**: Setup Game Structure
- **Task 2**: Implement Game Board  
- **Task 3**: Create Bubble Logic
- **Task 4**: Implement Player Controls
- **Task 5**: Game Mechanics
- **Task 6**: Game States
- **Task 7**: Audio and Effects
- **Task 8**: Responsive Design
- **Task 9**: Documentation
- **Task 10**: Testing

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Set `GROQ_API_KEY` environment variable
   - Restart the Streamlit app

2. **Rate Limits**
   - Wait a few minutes before retrying
   - Consider using a different model

3. **File Permission Errors**
   - Ensure write permissions in project directory
   - Run as administrator if needed

### Logs and Debugging

- Check the terminal output for detailed error messages
- Use the "Run Quick Tests" button to verify setup
- Monitor the project status panel for file changes

## Configuration

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Streamlit Configuration

The app uses these default settings:
- Port: 8501
- Address: 0.0.0.0 (accessible from network)
- Auto-reload: Enabled

## Development

### File Structure

```
streamlit_app.py          # Main Streamlit application
run_streamlit_ui.bat      # Windows batch launcher
run_streamlit_ui.ps1      # PowerShell launcher
agent/                    # Agent utilities and configurations
  bubble_shooter_tasks.md # Task definitions
  config.yaml            # Agent configuration
bubble-shooter-game/     # Generated game files
test_groq_*.py          # Test files
```

### Adding New Features

1. Edit `streamlit_app.py`
2. Add new task definitions to `agent/bubble_shooter_tasks.md`
3. Test using the built-in test runner

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review terminal output for errors
3. Verify API key and permissions
4. Test with simple tasks first

---

**Happy coding! 🎮**
