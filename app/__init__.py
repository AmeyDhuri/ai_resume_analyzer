import os
from flask import Flask, jsonify
from dotenv import load_dotenv
load_dotenv()
from app.config import Config
from app.extensions import db, migrate, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = "uploads"

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.resume.routes import resume_bp

    from app.auth import models
    from app.resume import models

    app.register_blueprint(main_bp)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.register_blueprint(resume_bp, url_prefix="/resume")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Route not found!"
        }), 404

    return app