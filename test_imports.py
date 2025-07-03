#!/usr/bin/env python3
"""
Simple test script to check if the app can import and start
"""

try:
    print("🔍 Testing imports...")
    
    print("  - Importing Flask components...")
    from flask import Flask
    print("  ✅ Flask imported")
    
    print("  - Importing database...")
    from utils.database import db
    print("  ✅ Database imported")
    
    print("  - Importing models...")
    from models.user import User
    from models.models import Task, Project
    print("  ✅ Models imported")
    
    print("  - Importing routes...")
    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.projects import projects_bp
    from routes.api import api_bp
    from routes.dashboard import dashboard_bp
    from routes.calendar import calendar_bp
    print("  ✅ Routes imported")
    
    print("  - Creating app...")
    from app import app
    print("  ✅ App created")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
