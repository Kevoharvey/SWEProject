import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))


def env_required(name):
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'farmmarket-secret-key-2026')
    MYSQL_HOST = env_required('MYSQL_HOST')
    MYSQL_USER = env_required('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = env_required('MYSQL_DB')
    MYSQL_CURSORCLASS = env_required('MYSQL_CURSORCLASS')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
