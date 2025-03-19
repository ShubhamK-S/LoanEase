from flask import render_template, redirect, url_for, request, jsonify, session, current_app, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app.models import LoanApplication, User
import os
import json
from datetime import datetime
from flask_wtf.csrf import generate_csrf

@bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if request.method == 'POST':
        email = request.form.get('email')
        # For demo purposes, create a user if they don't exist
        user = User.get(email)
        if not user:
            user = User(email)
            user.email = email
            user.name = email.split('@')[0]
            user.save()
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/start_application', methods=['POST'])
@login_required
def start_application():
    """Start a new loan application."""
    # Create a new application
    application = LoanApplication()
    application.save()
    
    # Store application ID in session
    session['application_id'] = application.id
    
    return redirect(url_for('main.application_process'))

@bp.route('/application')
def application_process():
    """Process loan application."""
    application_id = session.get('application_id')
    if not application_id:
        return redirect(url_for('main.index'))
    
    application = LoanApplication.load(application_id)
    if not application:
        return redirect(url_for('main.index'))
    
    # If face verification hasn't been completed, redirect to that step
    if not application.facial_verification:
        application.current_step = 'face_verification'
        application.save()
        return render_template('steps/face_verification.html', application=application)
    
    # Define step progress
    step_progress = {
        'personal_info': 25,
        'financial_info': 50,
        'documents': 75,
        'review': 100
    }
    
    # Set default step if none is defined
    if not application.current_step:
        application.current_step = 'personal_info'
        application.progress = step_progress['personal_info']
        application.save()
    
    # Update progress based on current step
    application.progress = step_progress.get(application.current_step, 0)
    application.save()
    
    # Skip to financial info if personal info is already provided
    if application.current_step == 'personal_info' and application.full_name:
        application.current_step = 'financial_info'
        application.progress = step_progress['financial_info']
        application.save()
    
    return render_template('application.html', application=application)

@bp.route('/api/update_step', methods=['POST'])
def update_step():
    """Update the current step of the application."""
    try:
        data = request.get_json()
        step = data.get('step')
        
        application_id = session.get('application_id')
        if not application_id:
            return jsonify({"error": "No active application"}), 400
        
        application = LoanApplication.load(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        application.current_step = step
        application.save()
        
        return jsonify({
            "success": True,
            "current_step": step
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/upload_document', methods=['POST'])
def upload_document():
    """Handle document upload."""
    try:
        application_id = session.get('application_id')
        if not application_id:
            return jsonify({"error": "No active application"}), 400
        
        application = LoanApplication.load(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        if 'document' not in request.files:
            return jsonify({"error": "No document provided"}), 400
        
        file = request.files['document']
        doc_type = request.form.get('type')
        
        if not doc_type:
            return jsonify({"error": "Document type not specified"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create a secure filename with application ID and timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{application_id}_{doc_type}_{timestamp}.pdf"
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(file_path)
            
            # Update application with document path
            setattr(application, doc_type, filename)
            application.save()
            
            return jsonify({
                "success": True,
                "message": "Document uploaded successfully",
                "filename": filename
            })
        
        return jsonify({"error": "Failed to upload document"}), 400
    except Exception as e:
        print(f"Error uploading document: {str(e)}")  # Add logging
        return jsonify({"error": str(e)}), 500

@bp.route('/api/upload_video', methods=['POST'])
def upload_video():
    """Handle video upload and processing."""
    try:
        application_id = session.get('application_id')
        if not application_id:
            return jsonify({"error": "No active application"}), 400
        
        application = LoanApplication.load(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        file = request.files['video']
        field = request.form.get('field')
        
        if not field:
            return jsonify({"error": "Field type not specified"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and file.filename.endswith('.webm'):
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create a secure filename with application ID and timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{application_id}_{field}_{timestamp}.webm"
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(file_path)
            
            # Update application with video path and field values
            if field == 'personal_info':
                # Update all personal information fields
                application.full_name = "Video Response"
                application.date_of_birth = "Video Response"
                application.email = "Video Response"
                application.phone = "Video Response"
                application.personal_info_video = filename
            elif field == 'financial_info':
                # Update all financial information fields
                application.monthly_income = "Video Response"
                application.employment_type = "Video Response"
                application.loan_amount = "Video Response"
                application.loan_purpose = "Video Response"
                application.financial_info_video = filename
            elif field == 'facial_verification':
                application.facial_verification = filename
            
            application.save()
            
            return jsonify({
                "success": True,
                "message": "Video uploaded successfully",
                "video_url": url_for('static', filename=f'videos/{filename}')
            })
        
        return jsonify({"error": "Invalid file type. Only .webm files are allowed"}), 400
    except Exception as e:
        print(f"Error uploading video: {str(e)}")  # Add logging
        return jsonify({"error": str(e)}), 500

@bp.route('/api/process_application', methods=['POST'])
def process_application():
    """Process the loan application and determine approval status."""
    try:
        application_id = session.get('application_id')
        if not application_id:
            return jsonify({"error": "No active application"}), 400
        
        application = LoanApplication.load(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        # Check if all required documents are uploaded
        required_docs = ['pan_card', 'id_proof', 'income_proof']
        has_all_docs = all(getattr(application, doc, None) for doc in required_docs)
        
        # Check if all required information is provided (including video responses)
        has_personal_info = all([
            application.full_name == "Video Response",
            application.date_of_birth == "Video Response",
            application.email == "Video Response",
            application.phone == "Video Response"
        ])
        
        has_financial_info = all([
            application.monthly_income == "Video Response",
            application.employment_type == "Video Response",
            application.loan_amount == "Video Response",
            application.loan_purpose == "Video Response"
        ])
        
        # Check if facial verification is completed
        has_facial_verification = bool(application.facial_verification)
        
        if not all([has_all_docs, has_personal_info, has_financial_info, has_facial_verification]):
            missing_items = []
            if not has_all_docs:
                missing_items.append("documents")
            if not has_personal_info:
                missing_items.append("personal information")
            if not has_financial_info:
                missing_items.append("financial information")
            if not has_facial_verification:
                missing_items.append("facial verification")
            
            return jsonify({
                "error": f"Missing required information: {', '.join(missing_items)}"
            }), 400
        
        # Process the application
        # For demo purposes, we'll approve if all documents are present
        application.status = 'approved'
        application.decision = 'Your loan application has been approved!'
        application.decision_reason = 'All required information and documents have been provided.'
        application.save()
        
        return jsonify({
            "success": True,
            "status": "approved",
            "message": "Your loan application has been approved! We will contact you shortly with further details."
        })
        
    except Exception as e:
        print(f"Error processing application: {str(e)}")  # Add logging
        return jsonify({"error": str(e)}), 500 