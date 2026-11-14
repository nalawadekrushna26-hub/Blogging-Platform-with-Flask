"""
Application Factory for the Blogging Platform.
Creates and configures the Flask application, initializes extensions,
and registers blueprints.
"""

import os
from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager


def create_app(config_class=Config):
    """Factory function to build and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory and instance directory exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions with the application instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Blueprints
    from app.auth import auth_bp
    from app.posts import posts_bp
    from app.main import main_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(main_bp)

    # Register Custom Error Handlers (403, 404, 500)
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Inject HTTP Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    return app
