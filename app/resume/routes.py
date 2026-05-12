import os
import logging
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

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
      original_filename = secure_filename(file.filename)

      unique_filename = (
         f"{uuid.uuid4()}_{original_filename}"
      )

      upload_path = os.path.join(
         current_app.config["UPLOAD_FOLDER"],
         unique_filename
      )
   
      file.save(upload_path)

      logging.info(
         "Resume uploaded by user %s: %s",
         current_user_id,
         unique_filename
      )

      return jsonify({
         "success": True,
         "message": "Resume uploaded successfully!",
         "data": {
            "original_filename": original_filename,
            "stored_filename": unique_filename,
            "upload_by": current_user_id
         }
      }),201
   
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

