"""
AI-Powered College Automation & Career Guidance System
Main Flask Application Factory
"""
from flask import Flask
from datetime import timedelta
from config import SECRET_KEY, DEBUG


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.permanent_session_lifetime = timedelta(hours=12)
    app.config['DEBUG'] = DEBUG

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.career import career_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(career_bp)

    return app
