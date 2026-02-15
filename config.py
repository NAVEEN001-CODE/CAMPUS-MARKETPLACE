import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus_marketplace_secret_key_2026')

    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'campus_marketplace')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_CURSORCLASS = 'DictCursor'

    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # AI Thresholds
    BLUR_THRESHOLD = 100.0        # Laplacian variance below this = blurry
    TRUST_SCORE_WEIGHTS = {
        'image_quality': 0.40,
        'condition': 0.40,
        'description': 0.20,
    }
