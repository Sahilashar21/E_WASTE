from flask import Flask, session, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os

# Load environment variables FIRST before importing routes that use them
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from datetime import datetime
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except Exception:
    BackgroundScheduler = None
    SCHEDULER_AVAILABLE = False

# Mongo setup
from mongo import mongo

# Blueprints
from routes.user_routes import user_bp
from routes.warehouse_routes import warehouse_bp
from routes.auth_routes import auth_bp
from routes.engineer_routes import engineer_bp
from routes.all_users_routes import all_users_bp
from routes.recycler_routes import recycler_bp
from routes.status_routes import status_bp
from routes.driver_routes import driver_bp
from routes.notification_routes import notification_bp
from routes.payment_routes import payment_bp

# Scheduled task: Reset engineer availability at midnight (12 AM)
def reset_engineer_availability():
    """Reset all engineer availability to True at midnight"""
    try:
        mongo.db.users.update_many(
            {"role": "engineer"},
            {"$set": {"available_tomorrow": True}}
        )
        print(f"[{datetime.now()}] Engineer availability reset for new day")
    except Exception as e:
        print(f"Error resetting engineer availability: {e}")

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/ewaste_db")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")

    # Initialize MongoDB
    mongo.init_app(app)

    # Initialize APScheduler for background tasks (optional)
    if SCHEDULER_AVAILABLE and BackgroundScheduler is not None:
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(func=reset_engineer_availability, trigger="cron", hour=0, minute=0)
            scheduler.start()
        except Exception as e:
            print(f"Failed to start scheduler: {e}")
    else:
        print("APScheduler not installed; skipping scheduled tasks (availability reset disabled).")

    # Register Blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(warehouse_bp, url_prefix="/warehouse")
    app.register_blueprint(auth_bp)
    app.register_blueprint(engineer_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(all_users_bp, url_prefix="/admin")
    app.register_blueprint(recycler_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(payment_bp)

    # Landing Route
    @app.route('/')
    def index():
        if 'user_id' in session:
            if session.get('role') == 'warehouse':
                return redirect(url_for('warehouse.dashboard'))
            elif session.get('role') == 'engineer':
                return redirect(url_for('engineer.dashboard'))
            elif session.get('role') == 'recycler':
                return redirect(url_for('recycler.dashboard'))
            elif session.get('role') == 'user':
                return redirect(url_for('user.dashboard'))
        return render_template('index.html')

    # Quick demo login for homepage "Try Demo" button
    @app.route('/dev/login')
    def dev_login():
        # Seed2 uses 'test_user_1' as a sample user id for demo pickup requests
        session['role'] = 'user'
        session['user_id'] = 'test_user_1'
        session['email'] = 'demo@example.com'
        session['name'] = 'Demo User'
        return redirect(url_for('user.dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
