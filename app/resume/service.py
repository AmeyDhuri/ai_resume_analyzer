import os
import uuid
from datetime import datetime
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

    ats_score = calculate_ats_score(parsed_text, skills)

    missing_skills = get_missing_skills(skills)

    feedback = generate_resume_feedback(ats_score)

    if resume.is_analyzed and resume.ai_feedback:
            ai_feedback = resume.ai_feedback

    else:
        ai_feedback = generate_ai_feedback(parsed_text)

        resume.ai_feedback = ai_feedback

        resume.is_analyzed = True

        resume.analyzed_at = datetime.utcnow()

        resume.ai_model = "pih3"

        resume.ats_score = ats_score

        db.session.commit()

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

def score_feedback(feedback):
    score = 0

    required_sections = ["Strengths", "Weaknesses", "Missing Skills", "ATS Tips", "Improvements"]

    for section in required_sections:
        if section in feedback:
            score += 10

    if len(feedback) < 2000:
        score += 10

    if feedback.count("##") >=2 :
        score +=10

    return score

def generate_best_feedback(parsed_text):
    responses = []

    for _ in range(3):
        feedback = generate_ai_feedback(parsed_text)

        responses.append(feedback)
    
    best_feedback = max(responses, key=score_feedback)

    return best_feedback

def analyze_job_match(resume_id, job_description):
    resume = Resume.query.get(resume_id)

    if not resume: 
        return None
    
    parse_text = parse_resume_text(resume)

    resume_skills = extracts_skills(parse_text)

    match_result = match_resume_to_job(resume_skills, job_description)

    fit_feedback = generate_job_fit_feedback(match_result["match_percentage"])

    return {
        "resume_skills": resume_skills,
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
        "match_percentage": match_result["match_percentage"],
        "fit_feedback": fit_feedback
    }