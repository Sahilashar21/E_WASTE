from flask import Blueprint, jsonify, session, redirect, request
from mongo import mongo
from bson import ObjectId
from datetime import datetime

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

@notification_bp.route('/my', methods=['GET'])
def my_notifications():
    """Fetch all notifications for current user"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    notifs = list(mongo.db.notifications.find({
        'recipient_id': user_id
    }).sort('created_at', -1).limit(20))
    
    # Convert ObjectId to string for JSON serialization
    for n in notifs:
        n['_id'] = str(n['_id'])
        n['created_at'] = n['created_at'].isoformat() if n.get('created_at') else None
    
    return jsonify(notifs)

@notification_bp.route('/<notif_id>/read', methods=['POST'])
def mark_read(notif_id):
    """Mark notification as read"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    mongo.db.notifications.update_one(
        {'_id': ObjectId(notif_id)},
        {'$set': {'read': True, 'read_at': datetime.utcnow()}}
    )
    
    return jsonify({'success': True})

@notification_bp.route('/unread-count', methods=['GET'])
def unread_count():
    """Get count of unread notifications for current user"""
    if not session.get('user_id'):
        return jsonify({'unread': 0})
    
    user_id = session['user_id']
    count = mongo.db.notifications.count_documents({
        'recipient_id': user_id,
        'read': False
    })
    
    return jsonify({'unread': count})

def create_notification(recipient_id, title, message, notification_type, related_data=None):
    """Helper to create a notification"""
    try:
        notif = {
            'recipient_id': recipient_id,
            'title': title,
            'message': message,
            'type': notification_type,  # 'cluster_assigned', 'engineer_coming', 'inspection_accepted', etc.
            'read': False,
            'related_data': related_data or {},
            'created_at': datetime.utcnow()
        }
        result = mongo.db.notifications.insert_one(notif)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None
