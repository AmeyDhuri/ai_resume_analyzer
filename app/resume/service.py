import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.resume.models import Resume
from app.utils.parser import extract_text_from_docx, extract_text_from_pdf, clean_resume_text
from app.utils.analyzer import extracts_skills, calculate_ats_score, get_missing_skills, generate_resume_feedback,match_resume_to_job, generate_job_fit_feedback
from app.ai.service import generate_ai_feedback

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

def analyze_resume(resume_id):
    resume = Resume.query.get(resume_id)

    if not resume:
        return None
    
    parsed_text = parse_resume_text(resume)

    skills = extracts_skills(parsed_text)

    ats_score = calculate_ats_score(skills)

    missing_skills = get_missing_skills(skills)

    feedback = generate_resume_feedback(ats_score)

    try:
        ai_feedback = generate_ai_feedback(parsed_text)

    except Exception as e:
        print(e)
        ai_feedback = "AI feedback unavailable"

    return {
        "resume": resume,
        "text": parsed_text,
        "skills": skills,
        "ats_score": ats_score, 
        "missing_skills": missing_skills,
        "feedback": feedback,
        "ai_feedback": ai_feedback
    }

def compare_resume_with_job(resume, job_description):
    parsed_text = parse_resume_text(resume)

    if not parsed_text:
        return None
    
    resume_skills = extracts_skills(parsed_text)

    matching_result = match_resume_to_job(resume_skills, job_description)
    
    feebdack = generate_job_fit_feedback(matching_result["match_percentage"])

    return {
        "resume_skills": resume_skills,
        "matched_skills": matching_result["matched_skills"],
        "missing_skills": matching_result["missing_skills"],
        "match_percentage": matching_result["match_percentage"],
        "feedback": feebdack
    }