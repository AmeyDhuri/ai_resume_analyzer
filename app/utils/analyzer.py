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