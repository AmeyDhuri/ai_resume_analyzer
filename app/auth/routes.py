import re
import logging 
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.auth.models import User
from app.auth.service import create_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required!"}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Invalid email format!"}), 400
    
    if len(password) <  6:
        return jsonify({"error": "Password must be at least 6 character"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists!"}), 400
    
    try:
        user = create_user(email, password)
        logging.info("User registered: %s", email)

    except Exception as e:
        db.session.rollback()
        logging.error("DB Error for %s: %s", email, {str(e)})
        return jsonify({"error": "Database error!"}), 500

    return jsonify({
        "success":True,
        "data": {
            "email": user.email
        },
        "message": "User successfully registered."
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required!"}), 400
    
    try:
        user = authenticate_user(email, password)

        if not user:
            logging.warning("Failed to login for %s", email)
            return jsonify({
                "success" : False,
                "message" : "Invalid email or pssword"
            }), 401
        
        logging.info("Use logged in %s", email)

        return jsonify({
            "success" : True,
            "data" :{
                "email" : user.email
            },
            "message" : "Login successful"
        }), 200
    
    except Exception as e:
        logging.error("Login error for %s : %s", email, str(e))

        return jsonify({
            "error" : "Internal server error"
        }), 500