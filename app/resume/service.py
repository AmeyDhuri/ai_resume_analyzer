import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.resume.models import Resume
from app.utils.parser import extract_text_from_docx, extract_text_from_pdf, clean_resume_text


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

def parse_resume_text(resume):
    file_path = resume.upload_path

    if resume.original_filename.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)

    elif resume.original_filename.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    
    else:
        return None
    
    cleaned_text = clean_resume_text(raw_text) 

    return cleaned_text
