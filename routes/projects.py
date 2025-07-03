from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.database import db
from models.models import Project, Task
from datetime import datetime, timedelta
import json

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def list_projects():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'active')
    sort_by = request.args.get('sort', 'created')
    
    query = Project.query.filter_by(user_id=current_user.id)
    
    if status_filter == 'active':
        query = query.filter_by(is_archived=False)
    elif status_filter == 'archived':
        query = query.filter_by(is_archived=True)
    
    # Sorting
    if sort_by == 'name':
        query = query.order_by(Project.name.asc())
    elif sort_by == 'created':
        query = query.order_by(Project.created_at.desc())
    elif sort_by == 'updated':
        query = query.order_by(Project.updated_at.desc())
    
    projects = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('projects/list.html', 
                         projects=projects,
                         status_filter=status_filter,
                         sort_by=sort_by)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        project = Project(
            name=data.get('name'),
            description=data.get('description'),
            color=data.get('color', '#3498db'),
            user_id=current_user.id
        )
        
        try:
            db.session.add(project)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'project': project.to_dict()})
            else:
                flash('Project created successfully!', 'success')
                return redirect(url_for('projects.view_project', id=project.id))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash('Error creating project. Please try again.', 'error')
    
    return render_template('projects/create.html')

@projects_bp.route('/<int:id>')
@login_required
def view_project(id):
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Get project statistics
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter_by(status='completed').count()
    active_tasks = project.tasks.filter_by(status='active').count()
    overdue_tasks = project.tasks.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).count()
    
    # Get recent tasks
    recent_tasks = project.tasks.order_by(Task.updated_at.desc()).limit(5).all()
    
    # Get tasks by priority
    priority_stats = {}
    for priority in ['low', 'medium', 'high', 'urgent']:
        priority_stats[priority] = project.tasks.filter_by(
            priority=priority, status='active'
        ).count()
    
    return render_template('projects/view.html', 
                         project=project,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         active_tasks=active_tasks,
                         overdue_tasks=overdue_tasks,
                         recent_tasks=recent_tasks,
                         priority_stats=priority_stats,
                         today=datetime.utcnow().date())

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.color = data.get('color', project.color)
        
        try:
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'project': project.to_dict()})
            else:
                flash('Project updated successfully!', 'success')
                return redirect(url_for('projects.view_project', id=project.id))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash('Error updating project. Please try again.', 'error')
    
    return render_template('projects/edit.html', 
                         project=project, 
                         total_tasks=project.tasks.count())

@projects_bp.route('/<int:project_id>/archive', methods=['POST'])
@login_required
def archive_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    try:
        project.is_archived = True
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'project': project.to_dict()})
        else:
            flash('Project archived successfully!', 'success')
            return redirect(url_for('projects.list_projects'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        else:
            flash('Error archiving project. Please try again.', 'error')
            return redirect(url_for('projects.view_project', project_id=project.id))

@projects_bp.route('/<int:project_id>/restore', methods=['POST'])
@login_required
def restore_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    try:
        project.is_archived = False
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'project': project.to_dict()})
        else:
            flash('Project restored successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=project.id))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        else:
            flash('Error restoring project. Please try again.', 'error')
            return redirect(url_for('projects.list_projects'))

@projects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Check if project has tasks
    if project.tasks.count() > 0:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Cannot delete project with existing tasks. Archive it instead.'}), 400
        else:
            flash('Cannot delete project with existing tasks. Archive it instead.', 'error')
            return redirect(url_for('projects.view_project', project_id=project.id))
    
    try:
        db.session.delete(project)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Project deleted successfully!', 'success')
            return redirect(url_for('projects.list_projects'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 400
        else:
            flash('Error deleting project. Please try again.', 'error')
            return redirect(url_for('projects.view_project', project_id=project.id))

@projects_bp.route('/<int:project_id>/tasks')
@login_required
def project_tasks(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    sort_by = request.args.get('sort', 'due_date')
    
    query = project.tasks
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
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
    
    return render_template('projects/tasks.html', 
                         project=project,
                         tasks=tasks,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         sort_by=sort_by)
