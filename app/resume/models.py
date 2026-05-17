from datetime import datetime
from app.extensions import db

class Resume(db.Model):
  __tablename__ = "resumes"


  id = db.Column(db.Integer, primary_key=True)
  original_filename = db.Column(db.String(255), nullable=False)
  stored_filename = db.Column(db.String(255), nullable=False)
  upload_path = db.Column(db.String(500), nullable=False)
  uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
