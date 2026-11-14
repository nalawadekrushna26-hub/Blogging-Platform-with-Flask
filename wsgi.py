"""
WSGI Entry Point for Production Deployment.
Used by production WSGI servers like Gunicorn, Waitress, or uWSGI.

Command for Linux/Cloud (Render, Railway, Heroku):
    gunicorn wsgi:app

Command for Windows:
    waitress-serve --port=5000 wsgi:app
"""

import os
from app import create_app, db
from config import config_by_name

# Select environment configuration (defaults to production if FLASK_ENV=production)
env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_by_name.get(env_name, config_by_name['default']))

# Ensure tables are ready in production database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
