from celery import Celery
import os

celery = Celery(
    "resume_analyzer",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)


import app.tasks.resume_tasks