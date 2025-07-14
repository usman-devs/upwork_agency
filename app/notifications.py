from app.events import send_notification
from app.models import User

def notify_user(user_id, message):
    """Helper function to send notifications"""
    send_notification(user_id, message)

def notify_admins(message):
    """Send notification to all admins"""
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        send_notification(admin.id, message)