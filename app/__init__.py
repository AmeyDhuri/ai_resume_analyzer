import os
import logging
from flask import Flask, jsonify

from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt, limiter, csrf, talisman


def create_app():
    app = Flask(__name__)
    from app.logging_config import logging
    config_name = os.getenv("FLASK_ENV", "development")

    if config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "uploads"
    )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    if app.config["DEBUG"]:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s"
    )

    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    talisman.init_app(app, force_https=False)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Invalid token"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Authorization token required"
        }), 401

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.resume.routes import resume_bp
    from app.admin.routes import admin_bp

    from app.auth import models
    from app.resume import models

    app.register_blueprint(main_bp)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.register_blueprint(resume_bp, url_prefix="/resume")

    app.register_blueprint(admin_bp, url_prefix="/admin")

    csrf.exempt(auth_bp)

    csrf.exempt(resume_bp)
    
    csrf.exempt(admin_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Route not found!"
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "success": False,
            "message": "File size exceeds upload limit"
        }), 413

    @app.errorhandler(429)
    def rate_limit_handler(error):
        return jsonify({
            "success": False,
            "message": "Too many requests. Please try again later"
        }), 429

    @app.errorhandler(500)
    def internal(error):
        return {
            "success": False,
            "message": "Internal server error"
        },500


    @app.errorhandler(403)
    def forbidden(error):
        return {
            "success": False,
            "message": "Access denied"
        },403

    return app