@echo off
echo 🚀 Starting Task Tracker Pro...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Start the application
echo 🌟 Starting Flask application...
echo 📱 Open http://localhost:5001 in your browser
echo ⏹️  Press Ctrl+C to stop the server
echo.

python app.py

pause
