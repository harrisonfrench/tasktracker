from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import calendar
from models.models import Task, Project

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

@calendar_bp.route('/')
@login_required
def view():
    """Display calendar view with tasks"""
    # Get current date or requested date
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get all tasks for the user with due dates
    tasks = Task.query.filter_by(user_id=current_user.id).filter(Task.due_date.isnot(None)).all()
    
    # Get all projects for color coding
    projects = Project.query.filter_by(user_id=current_user.id).all()
    project_colors = {project.id: project.color for project in projects}
    
    # Organize tasks by date
    tasks_by_date = {}
    for task in tasks:
        if task.due_date:
            date_key = task.due_date.strftime('%Y-%m-%d')
            if date_key not in tasks_by_date:
                tasks_by_date[date_key] = []
            tasks_by_date[date_key].append({
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'status': task.status,
                'project_id': task.project_id,
                'project_color': project_colors.get(task.project_id, '#3498db'),
                'time': task.due_date.strftime('%H:%M') if task.due_date.hour or task.due_date.minute else None
            })
    
    # Generate calendar data
    cal = calendar.Calendar(firstweekday=6)  # Start with Sunday
    month_days = cal.monthdayscalendar(year, month)
    
    # Previous and next month navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    current_date = datetime.now().date()
    selected_date = datetime(year, month, 1).date()
    
    return render_template('calendar/view.html',
                         month_days=month_days,
                         year=year,
                         month=month,
                         month_name=calendar.month_name[month],
                         tasks_by_date=tasks_by_date,
                         prev_year=prev_year,
                         prev_month=prev_month,
                         next_year=next_year,
                         next_month=next_month,
                         current_date=current_date,
                         selected_date=selected_date,
                         projects=projects)

@calendar_bp.route('/api/events/<int:year>/<int:month>')
@login_required
def get_events(year, month):
    """API endpoint to get calendar events for a specific month"""
    # Get start and end dates for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Get tasks within the date range
    tasks = Task.query.filter_by(user_id=current_user.id)\
                     .filter(Task.due_date >= start_date)\
                     .filter(Task.due_date <= end_date)\
                     .all()
    
    events = []
    for task in tasks:
        if task.due_date:
            events.append({
                'id': task.id,
                'title': task.title,
                'date': task.due_date.strftime('%Y-%m-%d'),
                'time': task.due_date.strftime('%H:%M') if task.due_date.hour or task.due_date.minute else None,
                'priority': task.priority,
                'status': task.status,
                'project_id': task.project_id,
                'url': f'/tasks/{task.id}'
            })
    
    return jsonify({'events': events})

@calendar_bp.route('/api/task/<int:task_id>')
@login_required
def get_task_details(task_id):
    """Get detailed task information for calendar popup"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'project': task.project.name if task.project else None,
        'project_color': task.project.color if task.project else '#3498db',
        'tags': [tag.name for tag in task.tags] if task.tags else []
    })
