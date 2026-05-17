import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.resume.service import save_resume_file

resume_bp = Blueprint("resume", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

def allowed_file(filename):
   return (
      "." in filename
      and
      filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
   )

@resume_bp.route("/uploads", methods=["POST"])
@jwt_required()
def test():
   
   current_user_id = get_jwt_identity()

   if "resume" not in request.files:
      return jsonify({
         "success": False,
         "message": "No file uploaded"
      }), 400
   
   file = request.files["resume"]

   if file.filename == "":
      return jsonify({
         "success": False,
         "message": "No selected file"
      }), 400
   
   if not allowed_file(file.filename):
      return jsonify({
         "success": False,
         "message": "Only PDF or DOCX files allowed"
      }), 400
   
   try:
      resume = save_resume_file(file, current_user_id)

      logging.info(
         "Resume uploaded by user %s: %s",
         current_user_id,
         resume["stored_filename"]
      )

      return jsonify({
         "success": True,
         "message": "Resume uploaded successfully",
         "data": {
            "resume_id": resume.id,
            "original_filename": (resume.original_filename),
            "stored_filename": (resume.stored_filename),
            "uploaded_by": resume.user_id
         }  
      }), 201
   
   except Exception as e:
      logging.error(
         "Upload failed for user %s: %s",
         current_user_id,
         str(e)
      )

      return jsonify({
         "success": False,
         "message": "File upload failed!"
      }), 500

