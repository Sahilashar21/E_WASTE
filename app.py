# from flask import Flask, session, redirect, render_template, request, url_for
# from dotenv import load_dotenv
# import os
# from datetime import datetime

# # Load environment variables FIRST
# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# # APScheduler (optional)
# try:
#     from apscheduler.schedulers.background import BackgroundScheduler
#     SCHEDULER_AVAILABLE = True
# except Exception:
#     BackgroundScheduler = None
#     SCHEDULER_AVAILABLE = False

# # Mongo setup (your existing hybrid mongo.py)
# from mongo import mongo

# # Blueprints
# from routes.user_routes import user_bp
# from routes.warehouse_routes import warehouse_bp
# from routes.auth_routes import auth_bp
# from routes.engineer_routes import engineer_bp
# from routes.all_users_routes import all_users_bp
# from routes.recycler_routes import recycler_bp
# from routes.status_routes import status_bp
# from routes.driver_routes import driver_bp
# from routes.notification_routes import notification_bp
# from routes.payment_routes import payment_bp


# def create_app():
#     app = Flask(__name__)

#     # ================= CONFIG =================

#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")

#     # 🔥 CRITICAL FIX: DB NAME MUST BE IN URI
#     app.config["MONGO_URI"] = os.getenv(
#         "MONGO_URI",
#         "mongodb+srv://darpanmeher1346_db_user:E8kreTF6Z8G5mFbn@cluster0.mhkyevr.mongodb.net/ewaste_db?retryWrites=true&w=majority"
#     )

#     # ================= INIT MONGO =================

#     mongo.init_app(app)

#     # ================= SCHEDULED TASK =================

#     def reset_engineer_availability():
#         """Reset all engineer availability to True at midnight"""
#         try:
#             mongo.db.users.update_many(
#                 {"role": "engineer"},
#                 {"$set": {"available_tomorrow": True}}
#             )
#             print(f"[{datetime.now()}] Engineer availability reset")
#         except Exception as e:
#             print(f"Error resetting engineer availability: {e}")

#     if SCHEDULER_AVAILABLE and BackgroundScheduler is not None:
#         try:
#             scheduler = BackgroundScheduler()

#             # 🔥 FIX: Ensure Flask app context exists
#             def scheduled_reset():
#                 with app.app_context():
#                     reset_engineer_availability()

#             scheduler.add_job(
#                 func=scheduled_reset,
#                 trigger="cron",
#                 hour=0,
#                 minute=0
#             )
#             scheduler.start()
#         except Exception as e:
#             print(f"Failed to start scheduler: {e}")
#     else:
#         print("APScheduler not installed; scheduled tasks disabled.")

#     # ================= BLUEPRINTS =================

#     app.register_blueprint(user_bp)
#     app.register_blueprint(warehouse_bp, url_prefix="/warehouse")
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(engineer_bp)
#     app.register_blueprint(driver_bp)
#     app.register_blueprint(notification_bp)
#     app.register_blueprint(all_users_bp, url_prefix="/admin")
#     app.register_blueprint(recycler_bp)
#     app.register_blueprint(status_bp)
#     app.register_blueprint(payment_bp)

#     # ================= ROUTES =================

#     @app.route('/')
#     def index():
#         if 'user_id' in session:
#             role = session.get('role')
#             if role == 'warehouse':
#                 return redirect(url_for('warehouse.dashboard'))
#             elif role == 'engineer':
#                 return redirect(url_for('engineer.dashboard'))
#             elif role == 'recycler':
#                 return redirect(url_for('recycler.dashboard'))
#             elif role == 'user':
#                 return redirect(url_for('user.dashboard'))
#         return render_template('index.html')

#     # Demo login
#     @app.route('/dev/login')
#     def dev_login():
#         session['role'] = 'user'
#         session['user_id'] = 'test_user_1'
#         session['email'] = 'demo@example.com'
#         session['name'] = 'Demo User'
#         return redirect(url_for('user.dashboard'))

#     return app


# # ================= ENTRY POINT =================

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True, port=5000)





from flask import Flask, session, redirect, render_template, url_for
from dotenv import load_dotenv
import os
from datetime import datetime

# Load env early
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# APScheduler (optional)
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except Exception:
    BackgroundScheduler = None
    SCHEDULER_AVAILABLE = False

# Mongo (DO NOT import blueprints yet)
from mongo import mongo


def create_app():
    app = Flask(__name__)

    # ================= CONFIG =================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")

    app.config["MONGO_URI"] = os.getenv(
        "MONGO_URI",
        "mongodb+srv://darpanmeher1346_db_user:E8kreTF6Z8G5mFbn@cluster0.mhkyevr.mongodb.net/ewaste_db?retryWrites=true&w=majority"
    )

    # ================= INIT MONGO =================
    mongo.init_app(app)

    # ================= HEALTH CHECK (DEBUG) =================
    @app.route("/__health")
    def health():
        return str(mongo.db), 200

    # ================= SCHEDULED TASK =================
    def reset_engineer_availability():
        try:
            mongo.db.users.update_many(
                {"role": "engineer"},
                {"$set": {"available_tomorrow": True}}
            )
            print(f"[{datetime.now()}] Engineer availability reset")
        except Exception as e:
            print("Scheduler error:", e)

    if SCHEDULER_AVAILABLE and BackgroundScheduler is not None:
        try:
            scheduler = BackgroundScheduler()

            def scheduled_reset():
                with app.app_context():
                    reset_engineer_availability()

            scheduler.add_job(
                func=scheduled_reset,
                trigger="cron",
                hour=0,
                minute=0
            )
            scheduler.start()
        except Exception as e:
            print("Scheduler failed:", e)

    # ================= IMPORT BLUEPRINTS (🔥 FIX) =================
    from routes.user_routes import user_bp
    from routes.warehouse_routes import warehouse_bp
    from routes.auth_routes import auth_bp
    from routes.engineer_routes import engineer_bp
    from routes.driver_routes import driver_bp
    from routes.notification_routes import notification_bp
    from routes.all_users_routes import all_users_bp
    from routes.recycler_routes import recycler_bp
    from routes.status_routes import status_bp
    from routes.payment_routes import payment_bp

    # ================= REGISTER BLUEPRINTS =================
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

    # ================= ROUTES =================
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'warehouse':
                return redirect(url_for('warehouse.dashboard'))
            elif role == 'engineer':
                return redirect(url_for('engineer.dashboard'))
            elif role == 'recycler':
                return redirect(url_for('recycler.dashboard'))
            elif role == 'user':
                return redirect(url_for('user.dashboard'))
        return render_template('index.html')

    return app


# ================= ENTRY POINT =================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
