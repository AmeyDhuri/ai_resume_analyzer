from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from app.config import Config
from app.extensions import db, migrate, jwt
import os



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.resume.routes import resume_bp

    app.register_blueprint(main_bp)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.register_blueprint(resume_bp, url_prefix="/resume")

    from app.auth import models

    return app