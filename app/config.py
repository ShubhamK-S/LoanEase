import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-prototype'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')
    APPLICATION_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'applications')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'your-gemini-api-key'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size