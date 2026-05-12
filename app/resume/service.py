import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def save_resume_file(file):
    original_filename = secure_filename(file.filname)

    unique_filename = (f"{uuid.uuid4()}_{original_name}")

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    file.save(upload_path)

    return{
        "original_filename": original_filename,
            "stored_filename": unique_filename,
            "upload_path": upload_path
    }