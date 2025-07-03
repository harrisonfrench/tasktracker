from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from models.models import Task, Project, UserAchievement
from utils.database import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Get user's statistics
    stats = get_user_stats()
    
    # Get recent tasks
    recent_tasks = Task.query.filter_by(user_id=current_user.id)\
                            .order_by(Task.updated_at.desc())\
                            .limit(5).all()
    
    # Get upcoming tasks (due within 7 days)
    upcoming_tasks = Task.query.filter(
        and_(
            Task.user_id == current_user.id,
            Task.status == 'active',
            Task.due_date.isnot(None),
            Task.due_date >= datetime.utcnow(),
            Task.due_date <= datetime.utcnow() + timedelta(days=7)
        )
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        and_(
            Task.user_id == current_user.id,
            Task.status == 'active',
            Task.due_date.isnot(None),
            Task.due_date < datetime.utcnow()
        )
    ).order_by(Task.due_date.asc()).all()
    
    # Get active projects with progress
    projects = Project.query.filter_by(user_id=current_user.id, is_archived=False)\
                           .order_by(Project.updated_at.desc()).limit(6).all()
    
    # Get recent achievements
    recent_achievements = UserAchievement.query.filter_by(user_id=current_user.id)\
                                              .order_by(UserAchievement.earned_at.desc())\
                                              .limit(3).all()
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_tasks=recent_tasks,
                         upcoming_tasks=upcoming_tasks,
                         overdue_tasks=overdue_tasks,
                         projects=projects,
                         recent_achievements=recent_achievements,
                         today=datetime.utcnow().date())

@dashboard_bp.route('/analytics')
@login_required
def analytics():
    # Get comprehensive analytics data
    analytics_data = get_analytics_data()
    return render_template('dashboard/analytics.html', data=analytics_data)

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    return jsonify(get_user_stats())

@dashboard_bp.route('/api/chart-data')
@login_required
def api_chart_data():
    return jsonify(get_chart_data())

def get_user_stats():
    user_id = current_user.id
    
    # Basic task counts
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()
    active_tasks = Task.query.filter_by(user_id=user_id, status='active').count()
    
    # Tasks by priority
    high_priority = Task.query.filter_by(user_id=user_id, priority='high', status='active').count()
    medium_priority = Task.query.filter_by(user_id=user_id, priority='medium', status='active').count()
    low_priority = Task.query.filter_by(user_id=user_id, priority='low', status='active').count()
    
    # Overdue tasks
    overdue_count = Task.query.filter(
        and_(
            Task.user_id == user_id,
            Task.status == 'active',
            Task.due_date.isnot(None),
            Task.due_date < datetime.utcnow()
        )
    ).count()
    
    # Projects
    total_projects = Project.query.filter_by(user_id=user_id, is_archived=False).count()
    
    # Completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tasks completed this week
    week_start = datetime.utcnow() - timedelta(days=7)
    tasks_this_week = Task.query.filter(
        and_(
            Task.user_id == user_id,
            Task.status == 'completed',
            Task.completed_at >= week_start
        )
    ).count()
    
    # Due today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    due_today = Task.query.filter(
        and_(
            Task.user_id == user_id,
            Task.status == 'active',
            Task.due_date >= today_start,
            Task.due_date < today_end
        )
    ).count()
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'active_tasks': active_tasks,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'overdue_count': overdue_count,
        'total_projects': total_projects,
        'completion_rate': round(completion_rate, 1),
        'tasks_this_week': tasks_this_week,
        'due_today': due_today,
        'user_level': current_user.level,
        'user_points': current_user.total_points,
        'current_streak': current_user.current_streak,
        'longest_streak': current_user.longest_streak,
        'progress_to_next_level': current_user.progress_to_next_level
    }

def get_chart_data():
    user_id = current_user.id
    
    # Tasks completed over time (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    daily_completions = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = Task.query.filter(
            and_(
                Task.user_id == user_id,
                Task.status == 'completed',
                Task.completed_at >= day_start,
                Task.completed_at < day_end
            )
        ).count()
        
        daily_completions.append({
            'date': day.strftime('%a'),
            'count': count
        })
    
    # Tasks by priority distribution
    priority_data = {
        'high': Task.query.filter_by(user_id=user_id, priority='high', status='active').count(),
        'medium': Task.query.filter_by(user_id=user_id, priority='medium', status='active').count(),
        'low': Task.query.filter_by(user_id=user_id, priority='low', status='active').count()
    }
    
    # Tasks by status
    status_data = {
        'completed': Task.query.filter_by(user_id=user_id, status='completed').count(),
        'active': Task.query.filter_by(user_id=user_id, status='active').count(),
        'cancelled': Task.query.filter_by(user_id=user_id, status='cancelled').count()
    }
    
    return {
        'daily_completions': daily_completions,
        'priority_distribution': priority_data,
        'status_distribution': status_data
    }

def get_analytics_data():
    user_id = current_user.id
    
    # Tasks completed over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_completions = db.session.query(
        func.date(Task.completed_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        and_(
            Task.user_id == user_id,
            Task.status == 'completed',
            Task.completed_at >= thirty_days_ago
        )
    ).group_by(func.date(Task.completed_at)).all()
    
    # Tasks by priority distribution
    priority_distribution = db.session.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).filter_by(user_id=user_id).group_by(Task.priority).all()
    
    # Project completion rates
    project_stats = []
    projects = Project.query.filter_by(user_id=user_id, is_archived=False).all()
    
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter_by(status='completed').count()
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        project_stats.append({
            'name': project.name,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round(completion_rate, 1),
            'color': project.color
        })
    
    # Recent achievements
    recent_achievements = UserAchievement.query.filter_by(user_id=user_id)\
                                              .order_by(UserAchievement.earned_at.desc())\
                                              .limit(10).all()
    
    return {
        'daily_completions': [{'date': item.date.isoformat(), 'count': item.count} 
                             for item in daily_completions],
        'priority_distribution': [{'priority': item.priority, 'count': item.count} 
                                 for item in priority_distribution],
        'project_stats': project_stats,
        'recent_achievements': [
            {
                'name': achievement.achievement_name,
                'description': achievement.description,
                'points': achievement.points_awarded,
                'earned_at': achievement.earned_at.isoformat()
            } for achievement in recent_achievements
        ]
    }
