from flask import Blueprint, jsonify
from mongo import mongo

status_bp = Blueprint('status', __name__)

@status_bp.route('/db_status')
def db_status():
    try:
        # Try to get server info to check connection
        mongo.cx.server_info()
        return jsonify({'status': 'connected'})
    except Exception as e:
        return jsonify({'status': 'disconnected', 'error': str(e)}), 500
