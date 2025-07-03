from flask_mail import Message
from flask import render_template

def init_notifications(app, mail):
    @app.route('/health')
    def health():
        return 'OK', 200

def send_task_reminder(user, task, mail):
    msg = Message(
        subject=f"Reminder: {task.title} due soon",
        sender='noreply@tasktracker.com',
        recipients=[user.email]
    )
    msg.html = f"""
    <h2>Task Reminder</h2>
    <p>Hi {user.full_name},</p>
    <p>This is a reminder that your task "{task.title}" is due soon.</p>
    <p>Due date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'No due date'}</p>
    <p>Priority: {task.priority.title()}</p>
    <p>Description: {task.description}</p>
    <p>Best regards,<br>Task Tracker Pro X Team</p>
    """
    mail.send(msg)
