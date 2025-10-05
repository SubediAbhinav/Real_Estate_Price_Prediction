import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db
from models.user import User
from auth.routes import auth_bp
from predict.routes import predict_bp  # <-- Import predict blueprint

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Absolute path for SQLite DB
db_path = os.path.join(os.path.dirname(__file__), "app.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
with app.app_context():
    db.init_app(app)
    db.create_all()
    print("DB created at:", db_path)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(predict_bp, url_prefix='/predict')  # <-- Register predict blueprint

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Optional health check
@app.route('/health')
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
