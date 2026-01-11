from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth_routes import login_required
from mongo import mongo

all_users_bp = Blueprint('all_users', __name__)

@all_users_bp.route('/users')
@login_required
def all_users_page():
    # Only allow admin or warehouse to view all users
    if session.get('role') not in ['admin', 'warehouse']:
        return redirect('/')

    users = list(mongo.db.users.find())
    return render_template('all_users.html', users=users, user_role=session.get('role'))
