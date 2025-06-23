@echo off
echo Starting Bubble Shooter Game Agent UI...
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
pause
