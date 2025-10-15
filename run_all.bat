@echo off
echo 🚀 Starting the complete project...

:: Start Flask (Python NLP Service)
start cmd /k "cd nlp_service && python app.py"

:: Wait 5 seconds for Flask to boot
timeout /t 5 >nul

:: Start Node backend
start cmd /k "cd backend && node backend.js"

echo ✅ Both Flask (8000) and Node (5000) are running!
echo 🌐 Open frontend/index.html in your browser to upload a PDF.
pause
