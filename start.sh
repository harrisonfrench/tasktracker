#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Task Tracker Pro..."

# Set production environment
export FLASK_ENV=production

# Create uploads directory if it doesn't exist
mkdir -p static/uploads

# Initialize database if needed
echo "📦 Initializing database..."
python -c "
from app import app
from utils.database import db
with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully!')
"

# Start the application
echo "🌐 Starting web server..."
if command -v gunicorn &> /dev/null; then
    exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app
else
    echo "⚠️  Gunicorn not found, using Flask development server"
    exec python app.py
fi
