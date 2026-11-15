"""
Entry point for running the Flask Blogging Platform application.
"""

from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    print("Starting Flask Blogging Platform on http://127.0.0.1:5000 ...")
    app.run(debug=True, host='127.0.0.1', port=5000)