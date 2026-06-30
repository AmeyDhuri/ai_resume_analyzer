from celery import Celery

celery = Celery(
    "resume_analyzer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

import app.tasks.resume_tasks