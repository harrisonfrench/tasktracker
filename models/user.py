from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from utils.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    
    # Account settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Preferences
    theme = db.Column(db.String(10), default='light')  # light, dark
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    slack_notifications = db.Column(db.Boolean, default=False)
    
    # Gamification
    total_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    level = db.Column(db.Integer, default=1)
    
    # Integration settings
    google_calendar_connected = db.Column(db.Boolean, default=False)
    slack_webhook_url = db.Column(db.String(255))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_activity(self):
        today = datetime.utcnow().date()
        
        if self.last_activity_date:
            if self.last_activity_date == today:
                return  # Already updated today
            
            if self.last_activity_date == today - timedelta(days=1):
                self.current_streak += 1
            else:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        self.last_activity_date = today
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
    
    def add_points(self, points):
        self.total_points += points
        self.update_level()
        self.update_activity()
    
    def update_level(self):
        # Simple leveling system: every 100 points = 1 level
        new_level = (self.total_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
            return True  # Level up occurred
        return False
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def progress_to_next_level(self):
        points_for_current_level = (self.level - 1) * 100
        points_for_next_level = self.level * 100
        current_progress = self.total_points - points_for_current_level
        return (current_progress / 100) * 100
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'theme': self.theme,
            'total_points': self.total_points,
            'level': self.level,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'progress_to_next_level': self.progress_to_next_level
        }
