"""
Advanced Notification System for Task Tracker Pro
Real-time notifications, smart alerts, and communication features
"""

from datetime import datetime, timedelta, timezone
from models.models import Notification, Task, Project
from models.user import User
from utils.database import db
from flask import current_app
from sqlalchemy import and_
import json

class NotificationManager:
    """Comprehensive notification management system"""
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type, action_url=None, priority='normal'):
        """Create a new notification for a user"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url
        )
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=user_id
        ).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications"""
        return Notification.query.filter_by(
            user_id=user_id, 
            is_read=False
        ).count()
    
    @staticmethod
    def get_recent_notifications(user_id, limit=10):
        """Get recent notifications for a user"""
        return Notification.query.filter_by(
            user_id=user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()

class SmartAlerts:
    """Intelligent alert system for proactive notifications"""
    
    @staticmethod
    def send_achievement_notification(user_id, achievement_name):
        """Send achievement unlock notification"""
        NotificationManager.create_notification(
            user_id=user_id,
            title=f"Achievement Unlocked: {achievement_name}!",
            message=f"Congratulations! You've unlocked the {achievement_name} achievement.",
            notification_type="achievement_unlocked",
            action_url="/dashboard"
        )
