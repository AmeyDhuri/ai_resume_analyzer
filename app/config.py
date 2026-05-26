import os 

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 *1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")