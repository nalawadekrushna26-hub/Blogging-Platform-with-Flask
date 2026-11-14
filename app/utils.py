"""
Helper utilities for the Blogging Platform.
Includes secure image upload management.
"""

import os
import secrets
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app


def save_image(form_picture, subfolder='uploads'):
    """
    Save an uploaded file securely with a randomized filename
    to avoid collisions and path traversal vulnerabilities.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_picture.filename))
    picture_filename = f"{random_hex}{f_ext.lower()}"
    destination_dir = Path(current_app.config['UPLOAD_FOLDER'])
    destination_dir.mkdir(parents=True, exist_ok=True)
    picture_path = destination_dir / picture_filename

    form_picture.save(picture_path)
    return picture_filename
