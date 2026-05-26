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
    "data analysis",
    "linux",
    "network security",
    "penetration testing",
    "figma",
    "ui ux",
    "excel",
    "communication",
    "teamwork"
]

def extracts_skills(text):
    text =  text.lower()

    found_skills = []

    for skill in COMMON_SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))

def calculate_ats_score(text, skills):
    text = text.lower()

    score = 0

    sections = [

        "skills",
        "education",
        "project",
        "experience",
        "certification",
        "summary"
    ]

    for section in sections:
        if section in text:
            score += 10

    skill_score = min(len(skills) * 2, 20)

    if "-" in text or "•"  in text:
        score += 10

    word_count = len(text.split())

    if 300 <= word_count <= 1200:
        score +=15

    project_keywords = [

        "project",
        "developed",
        "built",
        "created",
        "implemented"
    ]

    for kerword in project_keywords:
        if kerword in text:
            score += 2

    certification_keywords = [

        "certified",
        "certification",
        "aws",
        "oracle",
        "google"
    ]

    for keyword in certification_keywords:
        if kerword in text:
            score += 2
    
    if text.count("\n") > 10:
        score += 5 

    return min(round(score, 2), 100)

def get_missing_skills(skills):
    missing = []

    for skill in COMMON_SKILLS:
        if skill not in skills:
            missing.append(skill)

    return missing[:10]

def generate_resume_feedback(score):
    if score >= 85:
        return "Excellent resume profile"
    
    elif score >= 65:
        return "Good but can be improved"
    
    elif score >= 45:
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