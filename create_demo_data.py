#!/usr/bin/env python3
"""
Demo data generator for Task Tracker Pro
Creates sample projects, tasks, and achievements to showcase the application
"""

from app import app
from utils.database import db
from models.models import Task, Project, UserAchievement
from models.user import User
from datetime import datetime, timedelta, timezone
import random

def create_demo_data():
    with app.app_context():
        # Check if demo data already exists
        if User.query.filter_by(username='demo').first():
            print("Demo user already exists. Skipping...")
            return
        
        # Create a demo user if none exists
        demo_user = User.query.first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@tasktracker.com',
                first_name='Demo',
                last_name='User'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Created demo user (username: demo, password: demo123)")
        
        user_id = demo_user.id
        
        # Create sample projects
        projects_data = [
            {
                'name': 'Website Redesign',
                'description': 'Complete overhaul of company website with modern design and improved UX',
                'color': '#3b82f6'
            },
            {
                'name': 'Mobile App Development',
                'description': 'Cross-platform mobile application for iOS and Android',
                'color': '#10b981'
            },
            {
                'name': 'Marketing Campaign Q4',
                'description': 'End-of-year marketing push with social media and email campaigns',
                'color': '#f59e0b'
            },
            {
                'name': 'Database Migration',
                'description': 'Migrate legacy database to new cloud infrastructure',
                'color': '#ef4444'
            },
            {
                'name': 'Team Training Program',
                'description': 'Comprehensive training program for new technologies',
                'color': '#8b5cf6'
            }
        ]
        
        projects = []
        for project_data in projects_data:
            project = Project(
                user_id=user_id,
                **project_data,
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))
            )
            projects.append(project)
            db.session.add(project)
        
        db.session.commit()
        print(f"✅ Created {len(projects)} sample projects")
        
        # Create sample tasks
        task_templates = [
            {'title': 'Research competitor websites', 'priority': 'medium'},
            {'title': 'Create wireframes and mockups', 'priority': 'high'},
            {'title': 'Develop responsive layout', 'priority': 'high'},
            {'title': 'Implement user authentication', 'priority': 'urgent'},
            {'title': 'Set up database schema', 'priority': 'high'},
            {'title': 'Create API endpoints', 'priority': 'medium'},
            {'title': 'Design user interface', 'priority': 'medium'},
            {'title': 'Write unit tests', 'priority': 'low'},
            {'title': 'Deploy to staging server', 'priority': 'medium'},
            {'title': 'Performance optimization', 'priority': 'low'},
            {'title': 'User acceptance testing', 'priority': 'high'},
            {'title': 'Documentation update', 'priority': 'low'},
            {'title': 'Security audit', 'priority': 'urgent'},
            {'title': 'Content migration', 'priority': 'medium'},
            {'title': 'SEO optimization', 'priority': 'low'},
        ]
        
        statuses = ['todo', 'in_progress', 'completed']
        
        tasks_created = 0
        for project in projects:
            # Create 3-8 tasks per project
            num_tasks = random.randint(3, 8)
            for i in range(num_tasks):
                if tasks_created >= len(task_templates):
                    break
                    
                template = task_templates[tasks_created]
                status = random.choices(statuses, weights=[40, 30, 30])[0]
                
                # Create task with realistic dates
                created_date = project.created_at + timedelta(days=random.randint(0, 30))
                due_date = created_date + timedelta(days=random.randint(3, 21))
                
                task = Task(
                    user_id=user_id,
                    project_id=project.id,
                    title=template['title'],
                    description=f"Detailed description for {template['title'].lower()}",
                    priority=template['priority'],
                    status=status,
                    created_at=created_date,
                    due_date=due_date,
                    updated_at=created_date + timedelta(hours=random.randint(1, 48))
                )
                
                # Set completion date for completed tasks
                if status == 'completed':
                    task.completed_at = task.due_date - timedelta(days=random.randint(0, 3))
                
                db.session.add(task)
                tasks_created += 1
        
        db.session.commit()
        print(f"✅ Created {tasks_created} sample tasks")
        
        # Create sample achievements
        achievements_data = [
            {
                'achievement_type': 'first_task',
                'achievement_name': 'First Steps',
                'description': 'Created your first task',
                'points_awarded': 10
            },
            {
                'achievement_type': 'first_project',
                'achievement_name': 'Project Manager',
                'description': 'Created your first project',
                'points_awarded': 25
            },
            {
                'achievement_type': 'task_completion',
                'achievement_name': 'Getting Things Done',
                'description': 'Completed 10 tasks',
                'points_awarded': 50
            },
            {
                'achievement_type': 'streak',
                'achievement_name': 'Streak Master',
                'description': 'Completed tasks for 7 days in a row',
                'points_awarded': 100
            },
            {
                'achievement_type': 'milestone',
                'achievement_name': 'High Achiever',
                'description': 'Completed 50 tasks',
                'points_awarded': 200
            }
        ]
        
        for achievement_data in achievements_data:
            achievement = UserAchievement(
                user_id=user_id,
                **achievement_data,
                earned_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            )
            db.session.add(achievement)
        
        db.session.commit()
        print(f"✅ Created {len(achievements_data)} sample achievements")
        
        print("\n🎉 Demo data created successfully!")
        print("\n📝 Demo Login Credentials:")
        print("   Username: demo")
        print("   Password: demo123")
        print("\n🌐 Access the app at: http://localhost:5001")

if __name__ == '__main__':
    create_demo_data()
