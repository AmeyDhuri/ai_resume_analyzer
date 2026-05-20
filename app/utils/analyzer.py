COMMON_SKILLS = [
    "python",
    "flask",
    "django",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "html",
    "css",
    "javascript",
    "react",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "rest api",
    "machine learning",
    "data analysis"
]

def extracts_skills(text):
    text =  text.lower()

    found_skills = []

    for skill in COMMON_SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))

def calculate_ats_score(skills):
    max_score = len(COMMON_SKILLS)

    score = (len(skills) / max_score) * 100

    return round(score, 2)

def get_missing_skills(skills):
    missing = []

    for skill in COMMON_SKILLS:
        if skill not in skills:
            missing.append(skill)

    return missing

def generate_resume_feedback(score):
    if score >= 80:
        return "Excellent resume profile"
    
    elif score >= 60:
        return "Good but can be improved"
    
    elif score >= 40:
        return "Average resume needs more skills"
    
    else:
        return "Resume weak for ATS system"
    
def match_resume_to_job(resume_skills, job_description):
    job_description = job_description.lower()

    matched_skills = []

    missing_skills = []

    for skill in COMMON_SKILLS:
        if skill in job_description:
            if skill in resume_skills:
                matched_skills.append(skill)

            else:
                missing_skills.append(skill)

    total_required = (len(matched_skills) + len(missing_skills))

    if total_required == 0:
        match_percentage = 0

    else:
        match_percentage = (len(matched_skills) / total_required) * 100

    return {
        "matched_skills":matched_skills,
        "missing_skills":missing_skills,
        "match_percentage":round(match_percentage, 2)
    }

def generate_job_fit_feedback(match_percentage):
    if match_percentage >= 80:
        return "Excellent match fot this role"
    
    elif match_percentage >= 60:
        return "Good candidate match"
    
    elif match_percentage >= 40:
        return "Partial skill match"
    
    else:
        return "Low match for this role"