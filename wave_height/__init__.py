from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register routes within the app context
    with app.app_context():
        from . import routes  # Import routes here to register them with the app

    return app
