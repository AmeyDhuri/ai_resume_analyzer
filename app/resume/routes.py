import logging 
from app.extensions import limiter
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.resume.service import save_resume_file, get_user_resumes, get_resume_by_id, delete_resume, parse_resume_text, analyze_resume, compare_resume_with_job
from app.resume.models import Resume

resume_bp = Blueprint("resume", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

def allowed_file(filename):
   return (
      "." in filename
      and
      filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
   )

@resume_bp.route("/uploads", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def test():
   
   current_user_id = get_jwt_identity()

   if "resume" not in request.files:
      return jsonify({
         "success": False,
         "message": "No file uploaded"
      }), 400
   
   file = request.files["resume"]

   if file.mimetype not in ALLOWED_MIME_TYPES:
      return jsonify({
         "success": False,
         "message": "Invalid file type"
      }), 400

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

@resume_bp.route("/<int:resume_id>/analyze", methods=["GET"])
@jwt_required()
@limiter.limit("10 per hour")
def analyzer_resume_route(resume_id):
      current_user_id = get_jwt_identity()

      resume = get_resume_by_id(resume_id, current_user_id)

      if not resume:
         return jsonify({
            "success": False,
            "message": "Resume not found"
         }), 404
      
      analysis = analyze_resume(resume)

      return jsonify({
         "success": True,
         "data": analysis
      }), 200


@resume_bp.route("/<int:resume_id>/analysis", methods=["GET"])
def get_analysis(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.analysis_status != "completed":
        return jsonify({
            "success": False,
            "message": "Analysis not completed."
        }), 400

    result = analyze_resume(resume_id)

    return jsonify({
        "success": True,
        "resume_id": resume.id,
        "ats_score": result["ats_score"],
        "skills": result["skills"],
        "missing_skills": result["missing_skills"],
        "feedback": result["feedback"],
        "ai_feedback": result["ai_feedback"]
    }), 200

@resume_bp.route("/<int:resume_id>/match-job", methods=["POST"])
@jwt_required()
@limiter.limit("10 per hour")
def match_resume_to_job(resume_id):
   current_user_id = get_jwt_identity()

   resume = get_resume_by_id(resume_id, current_user_id)

   if not resume:
      return jsonify({
         "success": False,
         "message": "Resume not found"
      }), 400
   
   data = request.get_json()

   job_description = data.get("job_description")

   if not job_description:
      return jsonify({
         "success": False,
         "message": "Job description required"
      }), 400
   
   result = compare_resume_with_job(resume, job_description)

   return jsonify({
      "success": True,
      "data": result
   }), 200

@resume_bp.route("/<int:resume_id>/view", methods=["GET"])
@jwt_required()
def view_resume(resume_id):
   current_user_id = get_jwt_identity()

   resume = Resume.query.get(resume_id)

   if not resume:
      return jsonify({
         "success": False,
         "message": "Resume not found"
      }), 404 
   
   if resume.user_id != current_user_id:
      return jsonify({
         "success": False,
         "message": "Acess denied"
      }), 403
   
   return send_file(
      resume.upload_path,
      as_attachment=False
   )