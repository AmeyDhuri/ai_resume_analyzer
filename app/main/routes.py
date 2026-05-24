from flask import Blueprint, render_template, redirect, request, url_for, session, flash, current_app
import os
from werkzeug.utils import secure_filename
from app.resume.models import Resume
from app.resume.service import analyze_resume
from app.auth.models import User
from app.extensions import db

from app.auth.service import create_user, authenticate_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
  return redirect(url_for("main.login"))


@main_bp.route("/register", methods=["GET", "POST"])
def resgister():
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

      return redirect(url_for("main.dashboard"))
   
   return render_template("login.html")


@main_bp.route("/dashboard")
def dashboard():
   
   email = session.get("user_email")

   if not email:
      flash("Please login first", "warning")

      return redirect(url_for("main.login"))
   
   user = User.query.filter_by(email=email).first()

   resumes = Resume.query.filter_by(user_id=user.id).all()
   
   return render_template("dashboard.html", email=email, resumes=resumes)


@main_bp.route("/upload-resume", methods=["GET", "POST"])
def upload_resume():
   email = session.get("user_email")

   if not email:
      flash("Please login first", "danger")

      return redirect(url_for("main.login"))
   
   if request.method == "POST":
      
      file = request.files.get("resume")
      
      if not file:
            flash("No file selected!", "danger")

            return redirect(url_for("main.upload_resume"))
      filename = secure_filename(file.filename)

      upload_folder = current_app.config["UPLOAD_FOLDER"]

      os.makedirs(upload_folder, exist_ok=True)

      upload_path = os.path.join(upload_folder, filename)

      file.save(upload_path)

      user = User.query.filter_by(email=email).first()

      resume = Resume(original_filename=filename, stored_filename=filename, upload_path=upload_path, user_id=user.id)

      db.session.add(resume)
      db.session.commit()

      flash("Resume uploaded successfully!", "success")

      return redirect(url_for("main.dashboard"))

   return render_template("upload_resume.html")


@main_bp.route("/resume/<int:resume_id>/analyze")
def analyze_resume_page(resume_id):
   result = analyze_resume(resume_id)

   return render_template("resume_analysis.html", result=result)
