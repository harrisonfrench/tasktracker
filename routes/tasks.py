from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.database import db
from models.models import Task, Project
from datetime import datetime, timedelta
import json

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def list_tasks():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    project_filter = request.args.get('project', 'all')
    priority_filter = request.args.get('priority', 'all')
    sort_by = request.args.get('sort', 'due_date')
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if project_filter != 'all':
        query = query.filter_by(project_id=project_filter)
    
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    # Sorting
    if sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc())
    elif sort_by == 'priority':
        priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        query = query.order_by(
            db.case(priority_order, value=Task.priority).desc(),
            Task.due_date.asc()
        )
    elif sort_by == 'created':
        query = query.order_by(Task.created_at.desc())
    
    tasks = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
    
    return render_template('tasks/list.html', 
                         tasks=tasks, 
                         projects=projects,
                         status_filter=status_filter,
                         project_filter=project_filter,
                         priority_filter=priority_filter,
                         sort_by=sort_by)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Validate required fields
        if not data.get('title'):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Title is required'}), 400
            else:
                flash('Title is required', 'error')
                projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
                return render_template('tasks/create.html', projects=projects)
        
        if not data.get('project_id'):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Project is required'}), 400
            else:
                flash('Please select a project', 'error')
                projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
                return render_template('tasks/create.html', projects=projects)
        
        task = Task(
            title=data.get('title'),
            description=data.get('description'),
            project_id=int(data.get('project_id')),
            priority=data.get('priority', 'medium'),
            user_id=current_user.id,
            points_value=int(data.get('points_value', 10))
        )
        
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data.get('due_date').replace('Z', '+00:00'))
        
        if data.get('recurrence_pattern'):
            task.recurrence_pattern = data.get('recurrence_pattern')
            if data.get('recurrence_end_date'):
                task.recurrence_end_date = datetime.fromisoformat(data.get('recurrence_end_date').replace('Z', '+00:00'))
        
        try:
            db.session.add(task)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'task': task.to_dict()})
            else:
                flash('Task created successfully!', 'success')
                return redirect(url_for('tasks.list_tasks'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash('Error creating task. Please try again.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template('tasks/create.html', projects=projects)

@tasks_bp.route('/<int:id>')
@login_required
def view_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    subtasks_count = len(task.subtasks)
    attachments_count = len(task.attachments)
    return render_template('tasks/view.html', 
                         task=task,
                         subtasks_count=subtasks_count,
                         attachments_count=attachments_count)

@tasks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.project_id = data.get('project_id', task.project_id)
        task.priority = data.get('priority', task.priority)
        task.points_value = int(data.get('points_value', task.points_value))
        
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data.get('due_date').replace('Z', '+00:00'))
        elif data.get('due_date') == '':
            task.due_date = None
        
        task.recurrence_pattern = data.get('recurrence_pattern')
        if data.get('recurrence_end_date'):
            task.recurrence_end_date = datetime.fromisoformat(data.get('recurrence_end_date').replace('Z', '+00:00'))
        elif data.get('recurrence_end_date') == '':
            task.recurrence_end_date = None
        
        try:
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'task': task.to_dict()})
            else:
                flash('Task updated successfully!', 'success')
                return redirect(url_for('tasks.view_task', id=task.id))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash('Error updating task. Please try again.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template('tasks/edit.html', task=task, projects=projects)

@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    try:
        task.complete_task()
        db.session.commit()
        
        # Award points (handled by gamification system)
        from utils.gamification import award_points, check_achievements
        award_points(current_user.id, task.points_value, f"Completed task: {task.title}")
        check_achievements(current_user.id)
        
        if request.is_json:
            return jsonify({'success': True, 'task': task.to_dict()})
        else:
            flash(f'Task "{task.title}" completed! You earned {task.points_value} points.', 'success')
            return redirect(url_for('tasks.list_tasks'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        else:
            flash('Error completing task. Please try again.', 'error')
            return redirect(url_for('tasks.view_task', task_id=task.id))

@tasks_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Task deleted successfully!', 'success')
            return redirect(url_for('tasks.list_tasks'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        else:
            flash('Error deleting task. Please try again.', 'error')
            return redirect(url_for('tasks.view_task', task_id=task.id))

@tasks_bp.route('/bulk-action', methods=['POST'])
@login_required
def bulk_action():
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    action = data.get('action')
    
    if not task_ids or not action:
        return jsonify({'success': False, 'error': 'Missing task IDs or action'}), 400
    
    tasks = Task.query.filter(Task.id.in_(task_ids), Task.user_id == current_user.id).all()
    
    try:
        if action == 'complete':
            for task in tasks:
                task.complete_task()
        elif action == 'delete':
            for task in tasks:
                db.session.delete(task)
        elif action == 'change_priority':
            priority = data.get('priority')
            for task in tasks:
                task.priority = priority
        elif action == 'change_project':
            project_id = data.get('project_id')
            for task in tasks:
                task.project_id = project_id
        
        db.session.commit()
        return jsonify({'success': True, 'affected_count': len(tasks)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
