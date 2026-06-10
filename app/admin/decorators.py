from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.auth.models import User

def admin_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user:
            return jsonify({
                "success": False,
                "message": "User not found!"
            }), 404

        if current_user.role != "admin":
            return jsonify({
                "success": False,
                "message": "Admin access only!"
            }), 403
        
        return fn(*args, **kwargs)
    
    return wrapper