from flask import Blueprint, render_template, redirect, request, url_for, session, flash

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
   
   email =  session.get("user_email")

   if not email:
      flash("Please login first", "danger")

      return redirect(url_for("main.login"))
   
   return render_template("dashboard.html", email=email)