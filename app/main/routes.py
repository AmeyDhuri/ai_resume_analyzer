from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
  return jsonify({
      "success": True,
      "message": "API is running"
  }), 200