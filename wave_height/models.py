# wave_height/models.py
from . import db
#from werkzeug.security import generate_password_hash, check_password_hash

from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)  # Store plain-text password
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Set password directly
    def set_password(self, password):
        self.password_hash = password

    # Check password directly
    def check_password(self, password):
        return self.password_hash == password


class Interaction(db.Model):
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    data = db.Column(db.JSON)  # Store JSON data from the API

    user = db.relationship('User', backref=db.backref('interactions', lazy=True))
