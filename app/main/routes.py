import os
from sqlalchemy import func, text
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, redirect, request, url_for, session, flash, current_app, send_file, jsonify
from werkzeug.utils import secure_filename
from app.resume.models import Resume
from app.resume.service import analyze_resume, analyze_job_match, save_resume_file
from app.resume.routes import allowed_file
from app.auth.models import User
from app.extensions import db
from app.auth.service import create_user, authenticate_user
from app.admin.models import Auditlog
from app.admin.service import create_auditlog
from app.tasks.resume_tasks import analyze_resume_task
from app.forms.main_forms import ChangePasswordForm

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
  return redirect(url_for("main.login"))


@main_bp.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")

      try:
         create_user(email,password)

         flash("Registration successful!", "success")

         return redirect(url_for("main.login"))

      except Exception:
         flash("Registration failed!", "danger")

  return render_template("register.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
      email = request.form.get("email")
      password = request.form.get("password")

      user = authenticate_user(email, password)

      if not user:
         flash("Invalid credentials", "danger")

         return redirect(url_for("main.login"))

      session["user_email"] = user.email

      flash("Login successfully!", "success")

      return redirect(url_for("main.dashboard"))
   
   return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
   
   email = session.get("user_email")

   if not email:
      flash("Please login first", "warning")

      return redirect(url_for("main.login"))
   
   user = User.query.filter_by(email=email).first()

   search = request.args.get("search", "")

   sort = request.args.get("sort", "lastest")

   resumes_query = Resume.query.filter_by(user_id=user.id)

   if search:
      resumes_query = resumes_query.filter(Resume.original_filename.ilike(f"%{search}%"))
   
   if sort == "oldest":
      resumes = resumes_query.order_by(Resume.uploaded_at.asc()).all()

   else:
      resumes = resumes_query.order_by(Resume.uploaded_at.desc()).all()
   
   return render_template("dashboard.html", email=email, resumes=resumes, search=search)


@main_bp.route("/upload-resume", methods=["GET", "POST"])
def upload_resume():

    email = session.get("user_email")

    if not email:

        flash(
            "Please login first",
            "danger"
        )

        return redirect(
            url_for("main.login")
        )

    if request.method == "POST":

        file = request.files.get("resume")

        if not file or file.filename == "":
            flash(
                "No file selected!",
                "danger"
            )

            return redirect(
                url_for("main.upload_resume")
            )

        if not allowed_file(file.filename):

            flash(
               "Only PDF and DOCX files allowed",
               "danger"
            )

            return redirect(
               url_for("main.upload_resume")
            )
        
        user = User.query.filter_by(email=email).first()

        resume = save_resume_file(file, user.id)

        flash(
            "Resume uploaded successfully!",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "upload_resume.html"
    )


@main_bp.route("/resume/<int:resume_id>/analyze")
def analyze_resume_page(resume_id):
   analyze_resume_task.delay(resume_id)

   flash("Analysis started in background.", "success")

   return redirect(url_for("main.dashboard"))


@main_bp.route("/resume/<int:resume_id>/analysis")
def view_analysis(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.analysis_status != "completed":
        flash("Resume analysis is not completed yet.", "warning")
        return redirect(url_for("main.dashboard"))

    result = analyze_resume(resume_id)

    return render_template(
        "resume_analysis.html",
        result=result
    )


@main_bp.route("/resume/<int:resume_id>/job-match", methods=["GET", "POST"])
def job_match(resume_id):
      email = session.get("user_email")

      if not email:
         flash("Please login first", "warning")
         return redirect(url_for("main.login"))
      
      resume = Resume.query.get_or_404(resume_id)

      result =  None

      if request.method == "POST":
         job_description = request.form.get("job_description")

         result = analyze_job_match(resume_id, job_description)

      return render_template("job_match.html", resume=resume, result=result)

@main_bp.route("/admin/dashboard")
def admin_dashboard():
   email = session.get("user_email")

   if not email:
      flash("Please login first", "warning")
      return redirect(url_for("main.login"))
   
   user = User.query.filter_by(email=email).first()

   if user.role != "admin":
      flash("Admin access required", "danger")
      return redirect(url_for("main.dashboard"))
   
   scored_resumes = Resume.query.filter_by(
        is_analyzed=True
        ).all()

   average_ats_score = 0

   if scored_resumes:
        average_ats_score = round(
            sum(resume.ats_score for resume in scored_resumes)
            / len(scored_resumes),
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

   stats = {
      "total_users": User.query.count(),
      "total_resumes": Resume.query.count(),
      "analyzed_resumes": Resume.query.filter_by(is_analyzed=True).count(),
      "pending_analysis": Resume.query.filter_by(is_analyzed=False).count(),
      "average_ats_score": average_ats_score,
      "highest_ats_score": highest_ats_score,
      "uploads_per_user": user_uploads
   }

   return render_template("admin_dashboard.html", stats=stats)

@main_bp.route("/admin/users")
def admin_users():
   email = session.get("user_email")

   if not email:
      flash("Please login first", "danger")
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      flash("Admin access only", "danger")
      return redirect(url_for("main.dashboard"))
   
   users = User.query.order_by(User.id.asc()).all()

   return render_template("admin_users.html", users=users)

@main_bp.route("/admin/resumes")
def admin_resumes():
   email = session.get("user_email")

   if not email:
      flash("Please login first", "danger")
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      flash("Admin access only", "danger")
      return redirect(url_for("main.dashboard"))
   
   resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()

   return render_template("admin_resumes.html", resumes=resumes)

@main_bp.route("/admin/logs")
def admin_logs():
   email = session.get("user_email")

   if not email:
      flash("Please login first", "danger")
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      flash("Admin access only", "danger")
      return redirect(url_for("main.dashboard"))
   
   logs = Auditlog.query.order_by(Auditlog.created_at.desc()).all()

   return render_template("admin_logs.html", logs=logs)

@main_bp.app_context_processor
def inject_admin_status():

   email = session.get("user_email")

   if not email:
      return {"is_admin": False}

   user = User.query.filter_by(email=email).first()

   return {"is_admin": user and user.role == "admin"
}

@main_bp.route("/logout")
def logout():

   session.clear()

   flash("Logged out successfully", "success")

   return redirect(url_for("main.login"))

@main_bp.route("/change-password", methods=["GET", "POST"])
def change_password():

    email = session.get("user_email")

    if not email:
        flash("Please login first", "danger")
        return redirect(url_for("main.login"))

    user = User.query.filter_by(email=email).first()

    form = ChangePasswordForm()

    if form.validate_on_submit():

        if not check_password_hash(
            user.password,
            form.current_password.data
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("main.change_password"))

        if check_password_hash(
            user.password,
            form.new_password.data
        ):
            flash(
                "New password cannot be the same as your current password.",
                "warning"
            )
            return redirect(url_for("main.change_password"))

        user.password = generate_password_hash(
            form.new_password.data
        )

        db.session.commit()

        create_auditlog(admin_id=user.id, action="CHANGED PASSWORD", target=user.email)

        flash(
            "Password changed successfully.",   
            "success"
        )

        return redirect(url_for("main.dashboard"))

    return render_template(
        "change_password.html",
        form=form
    )

@main_bp.route("/admin/users/<int:user_id>/promote")
def promote_user(user_id):
   email = session.get("user_email")

   if not email:
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      return redirect(url_for("main.dashboard"))
   
   user =  User.query.get_or_404(user_id)

   user.role = "admin"

   db.session.commit()

   create_auditlog(admin_id=current_user.id, action="PROMOTE USER", target=user.email)

   flash("User promoted successfully", "success")
   return redirect(url_for("main.admin_users"))

@main_bp.route("/admin/users/<int:user_id>/demote")
def demote_user(user_id):
   email = session.get("user_email")

   if not email:
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      return redirect(url_for("main.dashboard"))
   
   user =  User.query.get_or_404(user_id)

   if user.id == current_user.id:
      flash("You cannot demote yourself", "danger")
      return redirect(url_for("main.admin_users"))

   user.role = "user"

   db.session.commit()

   create_auditlog(admin_id=current_user.id, action="DEMOTE USER", target=user.email)

   flash("User demoted successfully", "success")
   return redirect(url_for("main.admin_users"))

@main_bp.route("/admin/resumes/<int:resume_id>/delete", methods=["POST"])
def delete_resume(resume_id):
   email = session.get("user_email")

   if not email:
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   if current_user.role != "admin":
      return redirect(url_for("main.dashboard"))
   
   resume =  Resume.query.get_or_404(resume_id)

   if resume.upload_path and os.path.exists(resume.upload_path):
      os.remove(resume.upload_path)

   create_auditlog(admin_id=current_user.id, action="DELETE RESUME", target=f"Resume #{resume.id}")

   db.session.delete(resume)

   db.session.commit()

   flash("Resume deleted successfully", "success")
   return redirect(url_for("main.admin_resumes")) 

@main_bp.route("/resume/<int:resume_id>/view")
def view_resume(resume_id):
   email = session.get("user_email")

   if not email:
      return redirect(url_for("main.login"))
   
   current_user = User.query.filter_by(email=email).first()

   resume = Resume.query.get_or_404(resume_id)

   if resume.user_id != current_user.id:
      flash("Access denied!", "danger")
      return redirect(url_for("main.dashboard"))
   
   return send_file(
      resume.upload_path
   )

@main_bp.route("/health")
def healthy():

   try:

      db.session.execute(text("SELECT 1"))

      return jsonify({
         "status": "healthy",
         "database": "connected"
      }),200
   
   except Exception:
      return jsonify({
         "status": "unhealthy",
         "database": "disconnected"
      }),500