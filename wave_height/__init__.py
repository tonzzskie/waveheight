from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wave_user:incorrectpass@localhost/wave_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = 'root123'

    db.init_app(app)
    
    with app.app_context():
        from . import routes  # Import routes
        db.create_all()

    return app
