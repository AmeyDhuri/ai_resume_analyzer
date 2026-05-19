import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.resume.service import save_resume_file, get_user_resumes, get_resume_by_id, delete_resume, parse_resume_text

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
         resume.stored_filename
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
         "message": str(e)
      }), 500


@resume_bp.route("/my-resumes", methods=["GET"])
@jwt_required()
def my_resumes():
   current_user_id = get_jwt_identity()

   resumes = get_user_resumes(current_user_id)

   data = []

   for resume in resumes:
      data.append({
         "id": resume.id,
         "original_filename": (resume.original_filename),
         "stored_filename": (resume.stored_filename),
         "uploaded_at": (resume.uploaded_at)
      })

      
   return jsonify({
      "success": True,
      "count": len(data),
      "data": data
   }), 200


@resume_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id):
   current_user_id = get_jwt_identity()

   resume = get_resume_by_id(resume_id, current_user_id)

   if not resume:
      return jsonify({
         "success": False,
         "message": "Resume not found"
      }), 400
   
   return jsonify({
      "success": True,
      "data": {
         "id": resume.id,
         "original_filename": (resume.original_filename),
         "stored_filename": (resume.stored_filename),
         "uploaded_at": (resume.uploaded_at)
      }
   }), 200

@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required()
def remove_resume(resume_id):
   current_user_id = get_jwt_identity()

   deleted_resume = delete_resume(resume_id, current_user_id)

   if not deleted_resume:
      return jsonify({
         "session": False,
         "message": "Resume not found"
      }), 404
   
   return jsonify({
      "success": True,
      "message": ("Resume deleted successfully")
   }), 200

@resume_bp.route("/<int:resume_id>/parse", methods=["GET"])
@jwt_required()
def parse_resume(resume_id):
   current_user_id = get_jwt_identity()

   resume = get_resume_by_id(resume_id, current_user_id)

   if not resume :
      return jsonify({
         "success": False,
         "message": "Resume not found!"
      }), 404
   
   parsed_text = parse_resume_text(resume)

   return jsonify({
      "success": True,
      "data": {
         "resume_id": resume.id,
         "parsed_text": parsed_text
      }
   }), 200  