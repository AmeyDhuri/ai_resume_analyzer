from app.extensions import db
from zoneinfo import ZoneInfo
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))

    role = db.Column(db.String(20), nullable=False, default="user", server_default="user")

    resumes = db.relationship(
        "Resume",
        backref = "user",
        lazy = True,
        cascade="all, delete-orphan"
    )