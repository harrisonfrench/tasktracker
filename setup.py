#!/usr/bin/env python3
"""
Task Tracker Pro X - Setup and Initialization Script
This script initializes the database and creates sample data for development.
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from utils.database import db
from models.user import User
from models.models import Task, Project

def create_sample_user():
    """Create a sample user for testing."""
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(
            username='admin',
            email='admin@tasktrackerprox.com',
            first_name='Task',
            last_name='Admin',
            password_hash=generate_password_hash('admin123'),
            email_verified=True,
            total_points=500,
            level=3,
            current_streak=5
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created sample user: {user.username} (password: admin123)")
        return user
    else:
        print(f"ℹ️  Sample user already exists: {user.username}")
        return user

def create_sample_projects(user):
    """Create sample projects for the user."""
    projects_data = [
        {
            'name': 'Personal Website',
            'description': 'Build a new personal portfolio website with modern design',
            'color': '#e74c3c'
        },
        {
            'name': 'Mobile App Development',
            'description': 'Develop a task management mobile app for iOS and Android',
            'color': '#3498db'
        },
        {
            'name': 'Team Training Program',
            'description': 'Design and implement a comprehensive training program for new team members',
            'color': '#2ecc71'
        }
    ]
    
    created_projects = []
    for project_data in projects_data:
        existing = Project.query.filter_by(name=project_data['name'], user_id=user.id).first()
        if not existing:
            project = Project(
                user_id=user.id,
                **project_data
            )
            db.session.add(project)
            created_projects.append(project)
    
    db.session.commit()
    
    if created_projects:
        print(f"✅ Created {len(created_projects)} sample projects")
    else:
        print("ℹ️  Sample projects already exist")
    
    return Project.query.filter_by(user_id=user.id).all()

def create_sample_tasks(user, projects):
    """Create sample tasks for the user."""
    tasks_data = [
        {
            'title': 'Design homepage mockup',
            'description': 'Create wireframes and mockups for the homepage layout',
            'status': 'completed',
            'priority': 'high',
            'project_id': projects[0].id if projects else None,
            'due_date': datetime.utcnow() - timedelta(days=5)
        },
        {
            'title': 'Set up development environment',
            'description': 'Install and configure development tools and frameworks',
            'status': 'completed',
            'priority': 'high',
            'project_id': projects[0].id if projects else None,
            'due_date': datetime.utcnow() - timedelta(days=3)
        },
        {
            'title': 'Implement responsive CSS',
            'description': 'Add responsive design and mobile optimization',
            'status': 'active',
            'priority': 'medium',
            'project_id': projects[0].id if projects else None,
            'due_date': datetime.utcnow() + timedelta(days=2)
        },
        {
            'title': 'API research and planning',
            'description': 'Research backend technologies and plan API architecture',
            'status': 'active',
            'priority': 'medium',
            'project_id': projects[1].id if len(projects) > 1 else None,
            'due_date': datetime.utcnow() + timedelta(days=7)
        },
        {
            'title': 'Content strategy meeting',
            'description': 'Plan content structure and user experience flow',
            'status': 'active',
            'priority': 'low',
            'project_id': projects[2].id if len(projects) > 2 else None,
            'due_date': datetime.utcnow() + timedelta(days=10)
        },
        {
            'title': 'Code review and testing',
            'description': 'Review code quality and run comprehensive tests',
            'status': 'active',
            'priority': 'high',
            'project_id': projects[0].id if projects else None,
            'due_date': datetime.utcnow() + timedelta(days=1)
        }
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        # Skip tasks without valid project_id since it's required
        if task_data['project_id'] is None:
            continue
            
        existing = Task.query.filter_by(title=task_data['title'], user_id=user.id).first()
        if not existing:
            task = Task(
                user_id=user.id,
                **task_data
            )
            db.session.add(task)
            created_tasks.append(task)
    
    db.session.commit()
    
    if created_tasks:
        print(f"✅ Created {len(created_tasks)} sample tasks")
    else:
        print("ℹ️  Sample tasks already exist")

def main():
    """Main setup function."""
    print("🚀 Setting up Task Tracker Pro X...")
    print("=" * 50)
    
    # Create Flask app
    app, socketio = create_app()
    
    with app.app_context():
        # Create all database tables
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create sample data
        print("\n👤 Creating sample user...")
        user = create_sample_user()
        
        print("\n📁 Creating sample projects...")
        projects = create_sample_projects(user)
        
        print("\n📝 Creating sample tasks...")
        create_sample_tasks(user, projects)
        
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\n📋 Getting Started:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5001")
        print("3. Login with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n💡 Tip: Check out the sample projects and tasks created for you!")
        print("=" * 50)

if __name__ == '__main__':
    main()
