@echo off
echo 🚀 Starting Water Quality App...

:: Step 1: Start Streamlit app
start cmd /k "streamlit run water_quality_app_streamlit.py"

timeout /t 5

:: Step 2: Launch Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8501

pause
