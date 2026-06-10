import os
import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from app.extensions import db
from app.auth.models import User
from app.resume.models import Resume
from app.admin.decorators import admin_required
from app.admin.service import create_auditlog
from app.admin.models import Auditlog

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    total_users = User.query.count()

    total_resumes = Resume.query.count()

    analyzed_resumes = Resume.query.filter_by(
        is_analyzed=True
    ).count()

    pending_analysis = Resume.query.filter_by(
        is_analyzed=False
    ).count()

    scored_resumes = Resume.query.filter(
        Resume.ats_score.isnot(None)
    ).all()

    average_ats_score = 0

    if scored_resumes:

        average_ats_score = round(
            sum(
                resume.ats_score
                for resume in scored_resumes
            ) / len(scored_resumes),
            2
        )

    highest_resume = Resume.query.filter_by(is_analyzed=True).order_by(Resume.ats_score.desc()).first()

    highest_ats_score = (
        highest_resume.ats_score
        if highest_resume
        else 0
    )

    uploads_per_user = (
        db.session.query(
            User.email,
            func.count(Resume.id)
        )
        .join(
            Resume,
            User.id == Resume.user_id
        )
        .group_by(User.email)
        .all()
    )

    user_uploads = []

    for email, count in uploads_per_user:

        user_uploads.append({
            "email": email,
            "resume_count": count
        })

    return jsonify({
        "success": True,
        "data": {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "analyzed_resumes": analyzed_resumes,
            "pending_analysis": pending_analysis,
            "average_ats_score": average_ats_score,
            "highest_ats_score": highest_ats_score,
            "uploads_per_user": user_uploads
        }
    }), 200

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
  users = User.query.all()

  data = []

  for user in users:
    data.append({
      "id": user.id,
      "email": user.email,
      "role": user.role
    })

  return jsonify({
    "success": True,
    "count": len(data),
    "data": data
  }), 200

@admin_bp.route("/resumes", methods=["GET"])
@admin_required
def get_all_resumes():
  resumes =  Resume.query.all()

  data = []

  for resume in resumes:
      user = User.query.get(resume.user_id)
      
      data.append({
        "id": resume.id,
        "email": user.email,
        "original_filename" : resume.original_filename,
        "uploaded_at" : resume.uploaded_at,
        "is_analyzed" : resume.is_analyzed,
        "ats_score" : resume.ats_score,
      })
  
  return jsonify({
      "success": True,
      "count" : len(data),
      "data": data
  }), 200

@admin_bp.route("/resumes/<int:resume_id>", methods=["DELETE"])
@admin_required
def admin_delete_resume(resume_id):
    resume = Resume.query.get(resume_id)

    if not resume:
       return jsonify({
          "success": False,
          "message": "Resume not found!"
       }), 404
    
    try:
      if resume.upload_path and os.path.exists(resume.upload_path):
        os.remove(resume.upload_path)

      logging.warning(
          "Admin deleted resume %s",
          resume.id
      )

      create_auditlog(
          admin_id=int(get_jwt_identity()),
          action="DELETE_RESUME",
          target=f"Resume #{resume.id}"
      )

      db.session.delete(resume)
      db.session.commit()

      return jsonify({
        "success": True,
        "message": "Resume deleted successfully"
      }), 200
    
    except Exception as e:
      db.session.rollback()

      return jsonify({
         "success": False,
         "message": str(e)
      }), 500
    
@admin_bp.route("/users/<int:user_id>/promote", methods=["PATCH"])
@admin_required
def promote_user(user_id):
    user = User.query.get(user_id)

    if not user:
       return jsonify({
          "success": False,
          "message": "User not found!"
       }), 404
    
    try:
       if user.role == "admin":
          return jsonify({
             "success": False,
             "message": "User is already admin"
          }), 400
       
       logging.warning(
          "Admin promoted user %s",
          user.email
        )

       user.role = "admin"

       create_auditlog(
          admin_id=int(get_jwt_identity()),
          action="PROMOTE_USER",
          target=user.email
       )

       db.session.commit()

       return jsonify({
          "success": True,
          "message": "User promoted to admin"
       }), 200
       
    except Exception as e:
       db.session.rollback()
       return jsonify({
          "success": False,
          "message": str(e)
       }), 500
    
@admin_bp.route("/users/<int:user_id>/demote", methods=["PATCH"])
@admin_required
def demote_user(user_id):
    current_admin_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)

    if not user:
       return jsonify({
          "success": False,
          "message": "User not found!"
       }), 404
    
    try:
       if user.id == current_admin_id:
          return jsonify({
             "success": False,
             "message": "You cant demote yourself"
          }), 400

       if user.role == "user":
          return jsonify({
             "success": False,
             "message": "User already normal user"
          }), 400
       
       logging.warning(
          "Admin demoted user %s",
          user.email
        )

       user.role = "user"

       create_auditlog(
          admin_id=int(get_jwt_identity()),
          action="DEMOTE_USER",
          target=user.email
       )

       db.session.commit()

       return jsonify({
          "success": True,
          "message": "User demoted to admin"
       }), 200
       
    except Exception as e:
       db.session.rollback()
       return jsonify({
          "success": False,
          "message": str(e)
       }), 500

@admin_bp.route("/audit-logs", methods=["GET"])
@admin_required
def get_audit_logs():
   logs = Auditlog.query.order_by(Auditlog.created_at.desc()).all()

   data = []

   for log in logs:
      data.append({
         "id": log.id,
         "admin_id": log.admin_id,
         "action": log.action,
         "target": log.target,
         "created_at": log.created_at
      })

   return jsonify({
      "success": True,
      "count": len(data),
      "data": data
   }), 200