import os
from datetime import timedelta 
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 *1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class DevelopmentCofig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False