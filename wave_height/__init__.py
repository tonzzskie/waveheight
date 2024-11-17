from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv() 

db = SQLAlchemy()
oauth = OAuth()

# Replace os.getenv calls with direct assignment
GOOGLE_CLIENT_ID = "153261727313-2k9a11664psddano14edajktmpue51b0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wave_height_user:1wsowvdtCbVCMqPE73xC8JBLr2t3vQhl@dpg-csskksa3esus739nqor0-a.singapore-postgres.render.com/wave_height")


def create_app():
    app = Flask(__name__)

    # Database Configuration
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'DATABASE_URL'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wave_user:incorrectpass@localhost/wave_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = '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'

    db.init_app(app)
    oauth.init_app(app)

        # Configure Google OAuth using client credentials
    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        redirect_uri='http://localhost:5000/callback',
        client_kwargs={'scope': 'openid email profile'},
        server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
    )
    
    with app.app_context():
        from . import routes  # Import routes
        db.create_all()

    return app
