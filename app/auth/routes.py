import re
import logging 
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.auth.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.auth.service import create_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password required!"
        }), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({
            "success": False,
            "message": "Invalid email format!"
        }), 400
    
    if len(password) <  6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 character!"
        }), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({
            "success": False,
            "message": "User already exists!"
        }), 400
    
    try:
        user = create_user(email, password)
        logging.info("User registered: %s", email)

    except Exception as e:
        db.session.rollback()
        logging.error("DB Error for %s: %s", email, {str(e)})
        return jsonify({
            "success": False,
            "message": "Database error!"
            }), 500

    return jsonify({
        "success":True,
        "message": "User successfully registered.",
        "data": {
            "email": user.email
        },
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password required!"
        }), 400
    
    try:
        user = authenticate_user(email, password)

        if not user:
            logging.warning("Failed to login for %s", email)
            return jsonify({
                "success" : False,
                "message" : "Invalid email or pssword"
            }), 401
        
        access_token = create_access_token(
            identity=str(user.id)
        )

        logging.info("Use logged in %s", email)

        return jsonify({
            "success" : True,
            "token": access_token,
            "message" : "Login successful",
            "data" :{
                "id": user.id,
                "email" : user.email
            },
        }), 200
    
    except Exception as e:
        logging.error("Login error for %s : %s", email, str(e))

        return jsonify({
            "success": False,
            "message" : "Internal server error"
        }), 500
    
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()

    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found!"
        }), 404
    
    return jsonify({
        "success" :True,
        "message": "Profile fetched successfully",
        "data" :{
            "id": user.id,
            "email": user.email
        }
    }), 200