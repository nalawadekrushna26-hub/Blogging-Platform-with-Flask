"""
Application error handlers for HTTP 403, 404, and 500 error states.
"""

from flask import render_template
from app.extensions import db


def register_error_handlers(app):
    """Register custom error handlers with the Flask application instance."""

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden - permission denied."""
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found - resource or URL does not exist."""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error - rollback database session to prevent locks."""
        db.session.rollback()
        return render_template('errors/500.html'), 500
