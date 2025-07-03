import requests
import json

def sync_to_google_calendar(task, credentials):
    """Use google-api-python-client to insert events"""
    # Placeholder for Google Calendar sync
    pass

def post_slack_notification(task, webhook_url):
    """Use requests to post JSON payload"""
    if not webhook_url:
        return
    
    payload = {
        "text": f"Task Update: {task.title}",
        "attachments": [
            {
                "color": "good" if task.status == "completed" else "warning",
                "fields": [
                    {
                        "title": "Title",
                        "value": task.title,
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": task.status.title(),
                        "short": True
                    },
                    {
                        "title": "Priority",
                        "value": task.priority.title(),
                        "short": True
                    },
                    {
                        "title": "Due Date",
                        "value": task.due_date.strftime('%Y-%m-%d') if task.due_date else "No due date",
                        "short": True
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")
        return False
