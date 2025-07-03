from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.database import db
from models.models import Task, Project, TaskComment, UserAchievement
from models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def api_status():
    return {'status': 'Task Tracker Pro X API v1.0', 'timestamp': datetime.utcnow().isoformat()}

# Task API endpoints
@api_bp.route('/tasks', methods=['GET'])
@login_required
def api_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    project_id = request.args.get('project_id', type=int)
    priority = request.args.get('priority')
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    if project_id:
        query = query.filter_by(project_id=project_id)
    if priority:
        query = query.filter_by(priority=priority)
    
    tasks = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks.items],
        'pagination': {
            'page': tasks.page,
            'pages': tasks.pages,
            'per_page': tasks.per_page,
            'total': tasks.total,
            'has_next': tasks.has_next,
            'has_prev': tasks.has_prev
        }
    })

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def api_get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({'task': task.to_dict()})

@api_bp.route('/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description'),
        project_id=data.get('project_id'),
        priority=data.get('priority', 'medium'),
        user_id=current_user.id,
        points_value=data.get('points_value', 10)
    )
    
    if data.get('due_date'):
        try:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid due_date format'}), 400
    
    if data.get('recurrence_pattern'):
        task.recurrence_pattern = data['recurrence_pattern']
        if data.get('recurrence_end_date'):
            try:
                task.recurrence_end_date = datetime.fromisoformat(data['recurrence_end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid recurrence_end_date format'}), 400
    
    try:
        db.session.add(task)
        db.session.commit()
        return jsonify({'task': task.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    for field in ['title', 'description', 'priority', 'status', 'points_value']:
        if field in data:
            setattr(task, field, data[field])
    
    if 'project_id' in data:
        task.project_id = data['project_id']
    
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due_date format'}), 400
        else:
            task.due_date = None
    
    try:
        db.session.commit()
        return jsonify({'task': task.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Project API endpoints
@api_bp.route('/projects', methods=['GET'])
@login_required
def api_projects():
    projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return jsonify({
        'projects': [project.to_dict() for project in projects]
    })

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def api_get_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({'project': project.to_dict()})

@api_bp.route('/projects', methods=['POST'])
@login_required
def api_create_project():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    project = Project(
        name=data['name'],
        description=data.get('description'),
        color=data.get('color', '#3498db'),
        user_id=current_user.id
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        return jsonify({'project': project.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Analytics API endpoints
@api_bp.route('/analytics/overview', methods=['GET'])
@login_required
def api_analytics_overview():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic stats
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').count()
    active_projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).count()
    
    # Recent activity
    tasks_completed_this_week = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at >= week_ago
    ).count()
    
    tasks_completed_this_month = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at >= month_ago
    ).count()
    
    # Priority distribution
    priority_stats = {}
    for priority in ['low', 'medium', 'high', 'urgent']:
        priority_stats[priority] = Task.query.filter_by(
            user_id=current_user.id, priority=priority, status='active'
        ).count()
    
    # Overdue tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).count()
    
    return jsonify({
        'overview': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'active_projects': active_projects,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            'tasks_completed_this_week': tasks_completed_this_week,
            'tasks_completed_this_month': tasks_completed_this_month,
            'overdue_tasks': overdue_tasks
        },
        'priority_distribution': priority_stats
    })

@api_bp.route('/analytics/productivity', methods=['GET'])
@login_required
def api_analytics_productivity():
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily completion stats
    daily_stats = db.session.query(
        func.date(Task.completed_at).label('date'),
        func.count(Task.id).label('completed_tasks'),
        func.sum(Task.points_value).label('points_earned')
    ).filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at >= start_date
    ).group_by(func.date(Task.completed_at)).all()
    
    productivity_data = []
    for stat in daily_stats:
        productivity_data.append({
            'date': stat.date.isoformat(),
            'completed_tasks': stat.completed_tasks,
            'points_earned': stat.points_earned or 0
        })
    
    # Weekly patterns
    weekly_stats = db.session.query(
        extract('dow', Task.completed_at).label('day_of_week'),
        func.count(Task.id).label('completed_tasks')
    ).filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at >= start_date
    ).group_by(extract('dow', Task.completed_at)).all()
    
    weekly_pattern = {str(int(stat.day_of_week)): stat.completed_tasks for stat in weekly_stats}
    
    return jsonify({
        'productivity_data': productivity_data,
        'weekly_pattern': weekly_pattern
    })

@api_bp.route('/user/profile', methods=['GET'])
@login_required
def api_user_profile():
    total_points = current_user.total_points or 0
    achievements_count = UserAchievement.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'total_points': total_points,
            'achievements_count': achievements_count,
            'created_at': current_user.created_at.isoformat(),
            'level': (total_points // 100) + 1,
            'points_to_next_level': 100 - (total_points % 100)
        }
    })

@api_bp.route('/search', methods=['GET'])
@login_required
def api_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Search tasks
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        db.or_(
            Task.title.contains(query),
            Task.description.contains(query)
        )
    ).limit(10).all()
    
    # Search projects
    projects = Project.query.filter(
        Project.user_id == current_user.id,
        db.or_(
            Project.name.contains(query),
            Project.description.contains(query)
        )
    ).limit(5).all()
    
    return jsonify({
        'query': query,
        'results': {
            'tasks': [task.to_dict() for task in tasks],
            'projects': [project.to_dict() for project in projects]
        }
    })
