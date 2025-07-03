from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from flask_mail import Mail
from flask_socketio import SocketIO
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import Config
from utils.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mail = Mail(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.projects import projects_bp
    from routes.api import api_bp
    from routes.dashboard import dashboard_bp
    from routes.calendar import calendar_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(calendar_bp)
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('landing.html')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Task Tracker Pro X is running'}
    
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app, socketio

# Create the Flask app
app, socketio = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")
    
    port = int(os.environ.get('FLASK_RUN_PORT', 8082))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
