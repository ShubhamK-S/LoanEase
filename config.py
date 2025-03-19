import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///loanease.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    VIDEO_FOLDER = os.environ.get('VIDEO_FOLDER', 'app/static/videos')
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,webm').split(','))
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'LoanEase')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    APP_DESCRIPTION = os.environ.get('APP_DESCRIPTION', 'AI-Powered Loan Application System')
    
    # Video Configuration
    WELCOME_VIDEO = os.environ.get('WELCOME_VIDEO', 'welcome.mp4')
    PERSONAL_INFO_VIDEO = os.environ.get('PERSONAL_INFO_VIDEO', 'ask_name.mp4')
    FINANCIAL_INFO_VIDEO = os.environ.get('FINANCIAL_INFO_VIDEO', 'ask_income.mp4')
    LOAN_PURPOSE_VIDEO = os.environ.get('LOAN_PURPOSE_VIDEO', 'ask_loan_purpose.mp4')
    DOCUMENT_UPLOAD_VIDEO = os.environ.get('DOCUMENT_UPLOAD_VIDEO', 'ask_documents.mp4')
    PROCESSING_VIDEO = os.environ.get('PROCESSING_VIDEO', 'processing.mp4')
    APPROVED_VIDEO = os.environ.get('APPROVED_VIDEO', 'approved.mp4')
    REJECTED_VIDEO = os.environ.get('REJECTED_VIDEO', 'rejected.mp4')
    
    # Loan Application Settings
    MIN_LOAN_AMOUNT = int(os.environ.get('MIN_LOAN_AMOUNT', 10000))
    MAX_LOAN_AMOUNT = int(os.environ.get('MAX_LOAN_AMOUNT', 1000000))
    MIN_MONTHLY_INCOME = int(os.environ.get('MIN_MONTHLY_INCOME', 15000))
    MAX_MONTHLY_INCOME = int(os.environ.get('MAX_MONTHLY_INCOME', 1000000))
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    FACEPP_API_KEY = os.environ.get('FACEPP_API_KEY')
    FACEPP_API_SECRET = os.environ.get('FACEPP_API_SECRET') 