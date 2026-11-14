"""
Entry point for running the Flask Blogging Platform application.
"""

from app import create_app, db

# Create application instance using the factory
app = create_app()

# Automatically create SQLite tables if they do not exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Run the local development server
    print("Starting Flask Blogging Platform on http://127.0.0.1:5000 ...")
    app.run(debug=True, host='127.0.0.1', port=5000)
