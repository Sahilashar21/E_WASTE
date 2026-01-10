from flask import Flask, session, redirect
from mongo import mongo
from routes.user_routes import user_bp

app = Flask(__name__)
app.secret_key = "dev_secret"  # Required for session and flash messages
app.config["MONGO_URI"] = "mongodb://localhost:27017/ewaste_db"

# Initialize the Mock Database
mongo.init_app(app)

# Register your User Module
app.register_blueprint(user_bp)

@app.route('/')
def index():
    # Simple landing page to simulate login
    return """
    <h1>User Module Test Runner</h1>
    <p><a href="/dev/login">Click here to Login as User</a></p>
    """

@app.route('/dev/login')
def dev_login():
    session['role'] = 'user'
    session['user_id'] = 'test_user_1'
    return redirect('/user/dashboard')

if __name__ == '__main__':
    app.run(debug=True, port=5000)