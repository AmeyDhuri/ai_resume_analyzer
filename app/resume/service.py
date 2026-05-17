import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.resume.models import Resume


def save_resume_file(file, user_id):
    original_filename = secure_filename(file.filename)

    unique_filename = (f"{uuid.uuid4()}_{original_filename}")

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    file.save(upload_path)

    resume = Resume(
        original_filename=original_filename,
        stored_filename=unique_filename,
        upload_path=upload_path,
        user_id=user_id
    )

    db.session.add(resume)
    db.session.commit()

    return resume

def get_user_resumes(user_id):
    resumes = Resume.query.filter_by(user_id=user_id).all()

    return resumes

def get_resume_by_id(resume_id, user_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    return resume

def delete_resume(resume_id, user_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return None
    
    if os.path.exists(resume.upload_path):
        os.remove(resume.upload_path)

    db.session.delete(resume)
    db.session.commit()

    return resume