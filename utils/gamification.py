from models.user import UserAchievement
from utils.database import db

class GamificationSystem:
    ACHIEVEMENTS = {
        'first_task': {
            'name': 'Getting Started',
            'description': 'Complete your first task',
            'points': 10
        },
        'task_streak_7': {
            'name': 'Week Warrior',
            'description': 'Complete tasks for 7 days in a row',
            'points': 50
        },
        'task_streak_30': {
            'name': 'Monthly Master',
            'description': 'Complete tasks for 30 days in a row',
            'points': 200
        },
        'tasks_completed_10': {
            'name': 'Task Rookie',
            'description': 'Complete 10 tasks',
            'points': 25
        },
        'tasks_completed_50': {
            'name': 'Task Veteran',
            'description': 'Complete 50 tasks',
            'points': 100
        },
        'tasks_completed_100': {
            'name': 'Task Master',
            'description': 'Complete 100 tasks',
            'points': 250
        },
        'high_priority_master': {
            'name': 'Priority Pro',
            'description': 'Complete 20 high priority tasks',
            'points': 75
        },
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Complete a task before its due date',
            'points': 15
        },
        'level_5': {
            'name': 'Rising Star',
            'description': 'Reach level 5',
            'points': 50
        },
        'level_10': {
            'name': 'Elite User',
            'description': 'Reach level 10',
            'points': 100
        }
    }
    
    def __init__(self):
        pass
    
    def check_achievements(self, user, event_type, task=None):
        new_achievements = []
        if event_type == 'task_completed':
            new_achievements += self._check_task_completion_achievements(user, task)
        elif event_type == 'level_up':
            new_achievements += self._check_level_achievements(user)
        
        # Save new achievements
        for ach_key in new_achievements:
            ach_meta = self.ACHIEVEMENTS[ach_key]
            achievement = UserAchievement(
                user_id=user.id,
                achievement_type=ach_key,
                achievement_name=ach_meta['name'],
                description=ach_meta['description'],
                points_awarded=ach_meta['points']
            )
            user.add_points(ach_meta['points'])
            db.session.add(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

    def _check_task_completion_achievements(self, user, task):
        keys = []
        
        # First task
        total_completed = sum(1 for t in user.tasks if t.status == 'completed')
        if total_completed == 1:
            keys.append('first_task')
        
        # Streak achievements
        if user.current_streak == 7:
            keys.append('task_streak_7')
        if user.current_streak == 30:
            keys.append('task_streak_30')
        
        # Count completions
        if total_completed >= 10:
            keys.append('tasks_completed_10')
        if total_completed >= 50:
            keys.append('tasks_completed_50')
        if total_completed >= 100:
            keys.append('tasks_completed_100')
        
        # High priority
        high_completed = sum(1 for t in user.tasks if t.priority == 'high' and t.status == 'completed')
        if high_completed >= 20:
            keys.append('high_priority_master')
        
        # Early bird
        if task and task.completed_at and task.due_date and task.completed_at < task.due_date:
            keys.append('early_bird')
        
        return keys

    def _check_level_achievements(self, user):
        keys = []
        if user.level >= 5:
            keys.append('level_5')
        if user.level >= 10:
            keys.append('level_10')
        return keys
