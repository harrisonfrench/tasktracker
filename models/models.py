from datetime import datetime, timedelta
from utils.database import db
from sqlalchemy.ext.hybrid import hybrid_property
import json

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='projects')
    
    @hybrid_property
    def completion_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter_by(status='completed').count()
        return round((completed_tasks / total_tasks) * 100)
    
    @hybrid_property
    def active_tasks_count(self):
        return self.tasks.filter_by(status='active').count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'completion_percentage': self.completion_percentage,
            'active_tasks_count': self.active_tasks_count,
            'created_at': self.created_at.isoformat(),
            'is_archived': self.is_archived
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))  # For subtasks
    
    # Recurrence
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly, yearly
    recurrence_end_date = db.Column(db.DateTime)
    
    # Gamification
    points_value = db.Column(db.Integer, default=10)
    
    # Relationships
    user = db.relationship('User', backref='tasks')
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]))
    comments = db.relationship('TaskComment', backref='task', cascade='all, delete-orphan')
    attachments = db.relationship('TaskAttachment', backref='task', cascade='all, delete-orphan')
    
    @hybrid_property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return datetime.utcnow() > self.due_date
        return False
    
    @hybrid_property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    def complete_task(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
        # Create next recurrence if applicable
        if self.recurrence_pattern and (not self.recurrence_end_date or 
                                       datetime.utcnow() < self.recurrence_end_date):
            self.create_next_recurrence()
    
    def create_next_recurrence(self):
        if not self.recurrence_pattern:
            return
        
        next_due_date = self.calculate_next_due_date()
        if next_due_date:
            new_task = Task(
                title=self.title,
                description=self.description,
                due_date=next_due_date,
                priority=self.priority,
                project_id=self.project_id,
                user_id=self.user_id,
                recurrence_pattern=self.recurrence_pattern,
                recurrence_end_date=self.recurrence_end_date,
                points_value=self.points_value
            )
            db.session.add(new_task)
    
    def calculate_next_due_date(self):
        if not self.due_date or not self.recurrence_pattern:
            return None
        
        if self.recurrence_pattern == 'daily':
            return self.due_date + timedelta(days=1)
        elif self.recurrence_pattern == 'weekly':
            return self.due_date + timedelta(weeks=1)
        elif self.recurrence_pattern == 'monthly':
            return self.due_date + timedelta(days=30)  # Simplified
        elif self.recurrence_pattern == 'yearly':
            return self.due_date + timedelta(days=365)  # Simplified
        
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'project': self.project.to_dict() if self.project else None,
            'points_value': self.points_value,
            'subtasks_count': len(self.subtasks),
            'comments_count': len(self.comments)
        }

class TaskComment(db.Model):
    __tablename__ = 'task_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='task_comments')

class TaskAttachment(db.Model):
    __tablename__ = 'task_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='task_attachments')

class ProjectTemplate(db.Model):
    __tablename__ = 'project_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # software, marketing, design, etc.
    is_public = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Template data (JSON)
    template_data = db.Column(db.Text)  # JSON string with project structure
    
    # Foreign key
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='project_templates')

class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    task = db.relationship('Task', backref='time_logs')
    user = db.relationship('User', backref='time_logs')

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', backref='owned_teams')

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), default='member')  # owner, admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    team = db.relationship('Team', backref='members')
    user = db.relationship('User', backref='team_memberships')

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # task_due, achievement, mention, etc.
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='notifications')

class WorkflowTemplate(db.Model):
    __tablename__ = 'workflow_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    workflow_data = db.Column(db.Text)  # JSON with automation rules
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='workflow_templates')

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    dashboard_layout = db.Column(db.Text)  # JSON with widget preferences
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', uselist=False))

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    achievement_type = db.Column(db.String(50), nullable=False)
    achievement_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_awarded = db.Column(db.Integer, default=0)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='achievements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'achievement_type': self.achievement_type,
            'achievement_name': self.achievement_name,
            'description': self.description,
            'points_awarded': self.points_awarded,
            'earned_at': self.earned_at.isoformat(),
            'user_id': self.user_id
        }
