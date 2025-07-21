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
def api_productivity_analytics():
    """Get comprehensive productivity analytics"""
    from utils.analytics import AdvancedAnalytics
    
    days = request.args.get('days', 30, type=int)
    analytics = AdvancedAnalytics(current_user.id)
    insights = analytics.productivity_insights(days)
    
    return jsonify({
        'status': 'success',
        'data': insights,
        'period_days': days
    })

@api_bp.route('/analytics/time-tracking', methods=['GET'])
@login_required
def api_time_tracking_analytics():
    """Get time tracking analytics"""
    from utils.analytics import AdvancedAnalytics
    
    days = request.args.get('days', 30, type=int)
    analytics = AdvancedAnalytics(current_user.id)
    time_data = analytics.time_tracking_analysis(days)
    
    return jsonify({
        'status': 'success',
        'data': time_data,
        'period_days': days
    })

@api_bp.route('/analytics/workload-forecast', methods=['GET'])
@login_required
def api_workload_forecast():
    """Get upcoming workload forecast"""
    from utils.analytics import AdvancedAnalytics
    
    days = request.args.get('days', 14, type=int)
    analytics = AdvancedAnalytics(current_user.id)
    forecast = analytics.workload_forecast(days)
    
    return jsonify({
        'status': 'success',
        'data': forecast,
        'forecast_days': days
    })

# Notification API
@api_bp.route('/notifications', methods=['GET'])
@login_required
def api_notifications():
    """Get user notifications"""
    from utils.notifications import NotificationManager
    
    limit = request.args.get('limit', 10, type=int)
    notifications = NotificationManager.get_recent_notifications(current_user.id, limit)
    unread_count = NotificationManager.get_unread_count(current_user.id)
    
    return jsonify({
        'status': 'success',
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'action_url': n.action_url,
                'created_at': n.created_at.isoformat()
            } for n in notifications
        ],
        'unread_count': unread_count
    })

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read"""
    from utils.notifications import NotificationManager
    
    success = NotificationManager.mark_as_read(notification_id, current_user.id)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Notification marked as read' if success else 'Notification not found'
    })

# Advanced Task Management API
@api_bp.route('/tasks/bulk-update', methods=['POST'])
@login_required
def api_bulk_update_tasks():
    """Bulk update multiple tasks"""
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    updates = data.get('updates', {})
    
    if not task_ids or not updates:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    updated_count = 0
    for task_id in task_ids:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if task:
            for field, value in updates.items():
                if hasattr(task, field):
                    setattr(task, field, value)
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Updated {updated_count} tasks',
        'updated_count': updated_count
    })

@api_bp.route('/tasks/search', methods=['GET'])
@login_required
def api_search_tasks():
    """Advanced task search with filters"""
    query_text = request.args.get('q', '')
    project_ids = request.args.getlist('project_id', type=int)
    priorities = request.args.getlist('priority')
    statuses = request.args.getlist('status')
    due_date_start = request.args.get('due_date_start')
    due_date_end = request.args.get('due_date_end')
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    # Text search
    if query_text:
        query = query.filter(
            db.or_(
                Task.title.contains(query_text),
                Task.description.contains(query_text)
            )
        )
    
    # Filters
    if project_ids:
        query = query.filter(Task.project_id.in_(project_ids))
    if priorities:
        query = query.filter(Task.priority.in_(priorities))
    if statuses:
        query = query.filter(Task.status.in_(statuses))
    
    # Date range
    if due_date_start:
        start_date = datetime.fromisoformat(due_date_start)
        query = query.filter(Task.due_date >= start_date)
    if due_date_end:
        end_date = datetime.fromisoformat(due_date_end)
        query = query.filter(Task.due_date <= end_date)
    
    tasks = query.order_by(Task.due_date.asc()).limit(50).all()
    
    return jsonify({
        'status': 'success',
        'tasks': [task.to_dict() for task in tasks],
        'count': len(tasks)
    })

# Project Templates API
@api_bp.route('/project-templates', methods=['GET'])
@login_required
def api_project_templates():
    """Get available project templates"""
    from models.models import ProjectTemplate
    
    category = request.args.get('category')
    
    query = ProjectTemplate.query.filter(
        db.or_(
            ProjectTemplate.creator_id == current_user.id,
            ProjectTemplate.is_public == True
        )
    )
    
    if category:
        query = query.filter_by(category=category)
    
    templates = query.order_by(ProjectTemplate.usage_count.desc()).all()
    
    return jsonify({
        'status': 'success',
        'templates': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category,
                'usage_count': t.usage_count,
                'is_public': t.is_public,
                'creator': t.creator.username if t.creator else None
            } for t in templates
        ]
    })

@api_bp.route('/project-templates/<int:template_id>/use', methods=['POST'])
@login_required
def api_use_project_template(template_id):
    """Create project from template"""
    from models.models import ProjectTemplate
    
    template = ProjectTemplate.query.get_or_404(template_id)
    data = request.get_json()
    project_name = data.get('name', template.name)
    
    # Create project from template
    project = Project(
        name=project_name,
        description=template.description,
        user_id=current_user.id,
        color=data.get('color', '#3b82f6')
    )
    db.session.add(project)
    db.session.flush()
    
    # Create tasks from template
    if template.template_data:
        template_tasks = json.loads(template.template_data)
        for task_data in template_tasks.get('tasks', []):
            task = Task(
                title=task_data['title'],
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 'medium'),
                project_id=project.id,
                user_id=current_user.id,
                points_value=task_data.get('points_value', 10)
            )
            db.session.add(task)
    
    # Increment usage count
    template.usage_count += 1
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'project': project.to_dict(),
        'message': f'Project "{project_name}" created from template'
    })

# Time Tracking API
@api_bp.route('/time-tracking/start', methods=['POST'])
@login_required
def api_start_time_tracking():
    """Start time tracking for a task"""
    from models.models import TimeLog
    
    data = request.get_json()
    task_id = data.get('task_id')
    description = data.get('description', '')
    
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'}), 404
    
    # Stop any active time tracking
    active_logs = TimeLog.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    for log in active_logs:
        log.end_time = datetime.utcnow()
        log.duration_minutes = int((log.end_time - log.start_time).total_seconds() / 60)
        log.is_active = False
    
    # Start new time tracking
    time_log = TimeLog(
        task_id=task_id,
        user_id=current_user.id,
        start_time=datetime.utcnow(),
        description=description,
        is_active=True
    )
    db.session.add(time_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'time_log_id': time_log.id,
        'task_title': task.title,
        'started_at': time_log.start_time.isoformat()
    })

@api_bp.route('/time-tracking/stop', methods=['POST'])
@login_required
def api_stop_time_tracking():
    """Stop active time tracking"""
    from models.models import TimeLog
    
    data = request.get_json()
    time_log_id = data.get('time_log_id')
    
    if time_log_id:
        time_log = TimeLog.query.filter_by(
            id=time_log_id,
            user_id=current_user.id,
            is_active=True
        ).first()
    else:
        time_log = TimeLog.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
    
    if not time_log:
        return jsonify({'status': 'error', 'message': 'No active time tracking found'}), 404
    
    time_log.end_time = datetime.utcnow()
    time_log.duration_minutes = int((time_log.end_time - time_log.start_time).total_seconds() / 60)
    time_log.is_active = False
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'duration_minutes': time_log.duration_minutes,
        'duration_hours': round(time_log.duration_minutes / 60, 2),
        'task_title': time_log.task.title
    })

# Export/Import API
@api_bp.route('/export/tasks', methods=['GET'])
@login_required
def api_export_tasks():
    """Export tasks to JSON format"""
    format_type = request.args.get('format', 'json')
    project_id = request.args.get('project_id', type=int)
    
    query = Task.query.filter_by(user_id=current_user.id)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    tasks = query.all()
    
    export_data = {
        'export_date': datetime.utcnow().isoformat(),
        'user': current_user.username,
        'tasks': [
            {
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'status': task.status,
                'project_name': task.project.name,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            } for task in tasks
        ]
    }
    
    return jsonify({
        'status': 'success',
        'data': export_data,
        'task_count': len(tasks)
    })

# Dashboard Widgets API
@api_bp.route('/dashboard/widgets', methods=['GET'])
@login_required
def api_dashboard_widgets():
    """Get dashboard widget data"""
    
    # Quick stats
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').count()
    active_projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).count()
    
    # Recent activity
    recent_tasks = Task.query.filter_by(user_id=current_user.id)\
                            .order_by(Task.updated_at.desc())\
                            .limit(5).all()
    
    # Upcoming deadlines
    upcoming_tasks = Task.query.filter(
        db.and_(
            Task.user_id == current_user.id,
            Task.status == 'active',
            Task.due_date.isnot(None),
            Task.due_date >= datetime.utcnow(),
            Task.due_date <= datetime.utcnow() + timedelta(days=7)
        )
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    return jsonify({
        'status': 'success',
        'widgets': {
            'quick_stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'active_projects': active_projects
            },
            'recent_activity': [
                {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'updated_at': task.updated_at.isoformat(),
                    'project_name': task.project.name
                } for task in recent_tasks
            ],
            'upcoming_deadlines': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': task.due_date.isoformat(),
                    'priority': task.priority,
                    'project_name': task.project.name,
                    'days_until_due': (task.due_date - datetime.utcnow()).days
                } for task in upcoming_tasks
            ]
        }
    })
