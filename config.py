class Config:
    # Use the MySQL connection string with pymysql
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456789@localhost:3306/training'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications for performance
    SECRET_KEY = 'root123'  # Needed for session management (update with a secure key)
