"""
Advanced Analytics and Reporting Utilities for Task Tracker Pro
Provides comprehensive analytics, insights, and reporting capabilities
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, or_, extract
from models.models import Task, Project, UserAchievement, TimeLog
from models.user import User
from utils.database import db
import json

class AdvancedAnalytics:
    """Advanced analytics engine for comprehensive insights"""
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def productivity_insights(self, days=30):
        """Generate comprehensive productivity insights"""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Daily productivity metrics
        daily_stats = db.session.query(
            func.date(Task.completed_at).label('date'),
            func.count(Task.id).label('tasks_completed'),
            func.sum(Task.points_value).label('points_earned'),
            func.avg(
                func.julianday(Task.completed_at) - func.julianday(Task.created_at)
            ).label('avg_completion_time')
        ).filter(
            and_(
                Task.user_id == self.user_id,
                Task.status == 'completed',
                Task.completed_at >= start_date,
                Task.completed_at <= end_date
            )
        ).group_by(func.date(Task.completed_at)).all()
        
        # Peak productivity hours
        hourly_stats = db.session.query(
            extract('hour', Task.completed_at).label('hour'),
            func.count(Task.id).label('tasks_completed')
        ).filter(
            and_(
                Task.user_id == self.user_id,
                Task.status == 'completed',
                Task.completed_at >= start_date
            )
        ).group_by(extract('hour', Task.completed_at)).all()
        
        # Project performance analysis
        project_stats = db.session.query(
            Project.name,
            Project.color,
            func.count(Task.id).label('total_tasks'),
            func.sum(func.case([(Task.status == 'completed', 1)], else_=0)).label('completed_tasks'),
            func.avg(Task.points_value).label('avg_task_value'),
            func.sum(func.case([(Task.is_overdue == True, 1)], else_=0)).label('overdue_tasks')
        ).join(Task).filter(
            Project.user_id == self.user_id
        ).group_by(Project.id).all()
        
        return {
            'daily_productivity': [
                {
                    'date': stat.date.isoformat(),
                    'tasks_completed': stat.tasks_completed,
                    'points_earned': stat.points_earned or 0,
                    'avg_completion_time': round(stat.avg_completion_time or 0, 2)
                } for stat in daily_stats
            ],
            'peak_hours': [
                {
                    'hour': int(stat.hour),
                    'tasks_completed': stat.tasks_completed
                } for stat in hourly_stats
            ],
            'project_performance': [
                {
                    'name': stat.name,
                    'color': stat.color,
                    'total_tasks': stat.total_tasks,
                    'completed_tasks': stat.completed_tasks,
                    'completion_rate': round((stat.completed_tasks / stat.total_tasks * 100) if stat.total_tasks > 0 else 0, 1),
                    'avg_task_value': round(stat.avg_task_value or 0, 1),
                    'overdue_tasks': stat.overdue_tasks
                } for stat in project_stats
            ]
        }
    
    def time_tracking_analysis(self, days=30):
        """Analyze time tracking data for insights"""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        time_logs = db.session.query(
            TimeLog.task_id,
            Task.title,
            Project.name.label('project_name'),
            func.sum(TimeLog.duration_minutes).label('total_time'),
            func.count(TimeLog.id).label('sessions'),
            func.avg(TimeLog.duration_minutes).label('avg_session_time')
        ).join(Task).join(Project).filter(
            and_(
                TimeLog.user_id == self.user_id,
                TimeLog.start_time >= start_date,
                TimeLog.end_time.isnot(None)
            )
        ).group_by(TimeLog.task_id).all()
        
        return {
            'time_by_task': [
                {
                    'task_title': log.title,
                    'project_name': log.project_name,
                    'total_hours': round((log.total_time or 0) / 60, 2),
                    'sessions': log.sessions,
                    'avg_session_hours': round((log.avg_session_time or 0) / 60, 2)
                } for log in time_logs
            ],
            'total_tracked_hours': round(sum(log.total_time or 0 for log in time_logs) / 60, 2)
        }
    
    def achievement_progress(self):
        """Calculate progress towards potential achievements"""
        # Task completion milestones
        total_completed = Task.query.filter_by(
            user_id=self.user_id, 
            status='completed'
        ).count()
        
        # Streak calculation
        current_streak = self._calculate_current_streak()
        
        # Project completion rate
        projects = Project.query.filter_by(user_id=self.user_id).all()
        completed_projects = sum(1 for p in projects if p.completion_percentage == 100)
        
        return {
            'tasks_completed': total_completed,
            'current_streak': current_streak,
            'projects_completed': completed_projects,
            'milestones': {
                'task_novice': {'threshold': 10, 'current': total_completed, 'unlocked': total_completed >= 10},
                'task_expert': {'threshold': 50, 'current': total_completed, 'unlocked': total_completed >= 50},
                'task_master': {'threshold': 100, 'current': total_completed, 'unlocked': total_completed >= 100},
                'streak_starter': {'threshold': 3, 'current': current_streak, 'unlocked': current_streak >= 3},
                'streak_champion': {'threshold': 7, 'current': current_streak, 'unlocked': current_streak >= 7},
                'project_finisher': {'threshold': 5, 'current': completed_projects, 'unlocked': completed_projects >= 5}
            }
        }
    
    def _calculate_current_streak(self):
        """Calculate current daily completion streak"""
        today = datetime.now(timezone.utc).date()
        streak = 0
        current_date = today
        
        while True:
            completed_today = Task.query.filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.status == 'completed',
                    func.date(Task.completed_at) == current_date
                )
            ).count()
            
            if completed_today > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def workload_forecast(self, days=14):
        """Forecast upcoming workload based on due dates"""
        end_date = datetime.now(timezone.utc) + timedelta(days=days)
        
        upcoming_tasks = db.session.query(
            func.date(Task.due_date).label('date'),
            func.count(Task.id).label('task_count'),
            func.sum(func.case([(Task.priority == 'urgent', 1)], else_=0)).label('urgent_tasks'),
            func.sum(func.case([(Task.priority == 'high', 1)], else_=0)).label('high_tasks')
        ).filter(
            and_(
                Task.user_id == self.user_id,
                Task.status == 'active',
                Task.due_date.isnot(None),
                Task.due_date >= datetime.now(timezone.utc),
                Task.due_date <= end_date
            )
        ).group_by(func.date(Task.due_date)).all()
        
        return [
            {
                'date': task.date.isoformat(),
                'total_tasks': task.task_count,
                'urgent_tasks': task.urgent_tasks,
                'high_priority_tasks': task.high_tasks,
                'workload_intensity': 'high' if task.urgent_tasks > 2 else 'medium' if task.task_count > 3 else 'low'
            } for task in upcoming_tasks
        ]

class ReportGenerator:
    """Generate comprehensive reports in various formats"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.analytics = AdvancedAnalytics(user_id)
    
    def weekly_summary_report(self):
        """Generate a comprehensive weekly summary report"""
        # Get data for the past week
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        # Task completion stats
        completed_tasks = Task.query.filter(
            and_(
                Task.user_id == self.user_id,
                Task.status == 'completed',
                Task.completed_at >= start_date,
                Task.completed_at <= end_date
            )
        ).all()
        
        # Points earned
        total_points = sum(task.points_value for task in completed_tasks)
        
        # Projects worked on
        projects_worked = db.session.query(Project).join(Task).filter(
            and_(
                Task.user_id == self.user_id,
                Task.updated_at >= start_date
            )
        ).distinct().all()
        
        # Upcoming deadlines
        upcoming_deadlines = Task.query.filter(
            and_(
                Task.user_id == self.user_id,
                Task.status == 'active',
                Task.due_date.isnot(None),
                Task.due_date >= end_date,
                Task.due_date <= end_date + timedelta(days=7)
            )
        ).order_by(Task.due_date).all()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'achievements': {
                'tasks_completed': len(completed_tasks),
                'points_earned': total_points,
                'projects_active': len(projects_worked)
            },
            'productivity_insights': self.analytics.productivity_insights(7),
            'upcoming_deadlines': [
                {
                    'title': task.title,
                    'project': task.project.name,
                    'due_date': task.due_date.isoformat(),
                    'priority': task.priority,
                    'days_until_due': (task.due_date - end_date).days
                } for task in upcoming_deadlines
            ],
            'recommendations': self._generate_recommendations(completed_tasks, upcoming_deadlines)
        }
    
    def _generate_recommendations(self, completed_tasks, upcoming_deadlines):
        """Generate AI-like recommendations based on user data"""
        recommendations = []
        
        # Productivity recommendations
        if len(completed_tasks) < 3:
            recommendations.append({
                'type': 'productivity',
                'message': 'Consider breaking down larger tasks into smaller, manageable subtasks to increase completion rate.',
                'icon': 'target'
            })
        
        # Deadline management
        urgent_upcoming = [task for task in upcoming_deadlines if task.priority in ['urgent', 'high']]
        if len(urgent_upcoming) > 3:
            recommendations.append({
                'type': 'deadline',
                'message': f'You have {len(urgent_upcoming)} high-priority tasks due soon. Consider rescheduling or delegating some tasks.',
                'icon': 'clock'
            })
        
        # Workload balance
        if len(upcoming_deadlines) > 10:
            recommendations.append({
                'type': 'workload',
                'message': 'Your upcoming workload seems heavy. Consider using time-blocking techniques to manage your schedule better.',
                'icon': 'calendar'
            })
        
        # Achievement motivation
        user_achievements = UserAchievement.query.filter_by(user_id=self.user_id).count()
        if user_achievements < 3:
            recommendations.append({
                'type': 'gamification',
                'message': 'Complete more tasks to unlock achievements and earn points! Try setting daily completion goals.',
                'icon': 'award'
            })
        
        return recommendations
