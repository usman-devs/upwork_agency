from flask_socketio import emit
from app import socketio, db
from app.models import Notification

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def send_notification(user_id, message):
    """Send real-time notification to specific user"""
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    
    # Emit to specific user
    emit('new_notification', 
         notification.to_dict(), 
         room=f'user_{user_id}',
         namespace='/')