from flask_login import UserMixin
import json
import os
from datetime import datetime
from flask import current_app

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.email = None
        self.name = None
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get(cls, user_id):
        """Get user by ID."""
        try:
            filename = f"user_{user_id}.json"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            user = cls(data['id'])
            user.email = data.get('email')
            user.name = data.get('name')
            user.created_at = data.get('created_at')
            
            return user
        except Exception:
            return None

    def save(self):
        """Save user data to JSON file."""
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at
        }
        filename = f"user_{self.id}.json"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

class LoanApplication:
    def __init__(self, id=None):
        self.id = id or datetime.now().strftime('%Y%m%d%H%M%S')
        self.full_name = None
        self.date_of_birth = None
        self.email = None
        self.phone = None
        self.monthly_income = None
        self.employment_type = None
        self.loan_amount = None
        self.loan_purpose = None
        self.pan_card = None
        self.id_proof = None
        self.income_proof = None
        self.facial_verification = None
        self.personal_info_video = None
        self.financial_info_video = None
        self.current_step = 'personal_info'
        self.progress = 0
        self.status = 'pending'
        self.decision = None
        self.decision_reason = None
    
    def to_dict(self):
        """Convert application to dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth,
            'email': self.email,
            'phone': self.phone,
            'monthly_income': self.monthly_income,
            'employment_type': self.employment_type,
            'loan_amount': self.loan_amount,
            'loan_purpose': self.loan_purpose,
            'pan_card': self.pan_card,
            'id_proof': self.id_proof,
            'income_proof': self.income_proof,
            'facial_verification': self.facial_verification,
            'personal_info_video': self.personal_info_video,
            'financial_info_video': self.financial_info_video,
            'current_step': self.current_step,
            'progress': self.progress,
            'status': self.status,
            'decision': self.decision,
            'decision_reason': self.decision_reason
        }
    
    def save(self):
        """Save application data to JSON file."""
        data = self.to_dict()
        filename = f"{self.id}.json"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def load(cls, application_id):
        """Load application data from JSON file."""
        try:
            filename = f"{application_id}.json"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            application = cls(data['id'])
            for key, value in data.items():
                setattr(application, key, value)
            
            return application
        except Exception:
            return None