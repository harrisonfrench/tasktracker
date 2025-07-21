#!/bin/bash

# Task Tracker Pro - Quick Start Script
echo "🚀 Starting Task Tracker Pro..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ ! -f ".last_install" ] || [ "requirements.txt" -nt ".last_install" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch .last_install
fi

# Start the application
echo "🌟 Starting Flask application..."
echo "📱 Open http://localhost:5001 in your browser"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python app.py
