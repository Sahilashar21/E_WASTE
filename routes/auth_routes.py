from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from mongo import mongo
from functools import wraps
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect('/')
        return render_template('login.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = mongo.db.users.find_one({'email': email})
    
    # Check password using werkzeug (handles both hashed and plain text)
    if user:
        stored_password = user.get('password', '')
        # Try hashed password first (werkzeug format)
        if stored_password.startswith('pbkdf2:') or stored_password.startswith('scrypt:'):
            password_valid = check_password_hash(stored_password, password)
        else:
            # Fallback to plain text comparison for backwards compatibility
            password_valid = stored_password == password
        
        if password_valid:
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['role'] = user['role']
            session['name'] = user.get('name', '')

            # Redirect based on role
            if user['role'] == 'warehouse':
                return redirect(url_for('warehouse.dashboard'))
            elif user['role'] == 'engineer':
                return redirect(url_for('engineer.dashboard'))
            elif user['role'] == 'recycler':
                return redirect(url_for('recycler.dashboard'))
            elif user['role'] == 'user':
                return redirect(url_for('user.dashboard'))
            elif user['role'] == 'driver':
                return redirect(url_for('driver.dashboard'))
            else:
                return redirect('/')

    # Development fallback: if DB not seeded, allow demo credentials
    DEMO_USERS = {
        'user@example.com': ('user', 'userpass', 'Demo User'),
        'warehouse@example.com': ('warehouse', 'warehousepass', 'Main Warehouse Admin'),
        'engineer@example.com': ('engineer', 'password123', 'Demo Engineer'),
        'engineer1@example.com': ('engineer', 'engineerpass', 'Ramesh Engineer'),
        'recycler@example.com': ('recycler', 'password123', 'Demo Recycler'),
        'driver@example.com': ('driver', 'password123', 'Demo Driver')
    }

    demo = DEMO_USERS.get(email)
    if demo and demo[1] == password:
        session['user_id'] = email
        session['email'] = email
        session['role'] = demo[0]
        session['name'] = demo[2]

        if demo[0] == 'warehouse':
            return redirect(url_for('warehouse.dashboard'))
        elif demo[0] == 'engineer':
            return redirect(url_for('engineer.dashboard'))
        elif demo[0] == 'recycler':
            return redirect(url_for('recycler.dashboard'))
        elif demo[0] == 'driver':
            return redirect(url_for('driver.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    flash('Invalid email or password', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = 'user' # Default role for self-registration

    if mongo.db.users.find_one({'email': email}):
        flash('Email already registered', 'error')
        return redirect(url_for('auth.register'))

    from werkzeug.security import generate_password_hash
    mongo.db.users.insert_one({
        'name': name,
        'email': email,
        'password': generate_password_hash(password),
        'role': role
    })
    flash('Registration successful! Please login.', 'success')
    return redirect(url_for('auth.login'))