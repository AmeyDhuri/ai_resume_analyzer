from app.celery_app import celery
from app import create_app
from app.resume.models import Resume
from app.resume.service import analyze_resume
from app.extensions import db


@celery.task
def analyze_resume_task(resume_id):
    app = create_app()

    with app.app_context():
        resume = Resume.query.get(resume_id)

        if not resume:
            return "Resume not found"

        try:
            resume.analysis_status = "processing"
            db.session.commit()

            analyze_resume(resume_id)

            resume.analysis_status = "completed"
            db.session.commit()

            return f"Resume {resume_id} analyzed"

        except Exception as e:
            resume.analysis_status = "failed"
            db.session.commit()

            raise e