from app.extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo

class Auditlog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(255), nullable= False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))