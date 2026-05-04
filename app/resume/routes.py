from flask import Blueprint

resume_bp = Blueprint("resume", __name__)

@resume_bp.route("/")
def test():
   return "Resume module working"