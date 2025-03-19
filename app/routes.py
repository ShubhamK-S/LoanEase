import os
import json
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, session
from werkzeug.utils import secure_filename
from app.models import LoanApplication
from app.utils.document_processor import extract_document_info
from app.utils.facial_verification import verify_face_consistency
from app.utils.loan_eligibility import calculate_eligibility
from app.facial_verification.face_verifier import FaceVerifier
import time

main = Blueprint('main', __name__)
face_verifier = FaceVerifier()

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webm'}

@main.route('/api/register_face', methods=['POST'])
def register_face():
    """Register a user's face for future verification."""
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file and allowed_file(file.filename):
        image_data = file.read()
        success, message = face_verifier.store_face(image_data, application_id)
        return jsonify({"success": success, "message": message})
    
    return jsonify({"error": "Invalid file type"}), 400

@main.route('/api/verify_face', methods=['POST'])
def verify_face():
    """Verify a user's identity using facial recognition."""
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file and allowed_file(file.filename):
        image_data = file.read()
        success, message = face_verifier.verify_identity(image_data, application_id)
        
        # Update application with verification status
        application.facial_verification = success
        application.save()
        
        return jsonify({"success": success, "message": message})
    
    return jsonify({"error": "Invalid file type"}), 400

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/start', methods=['POST'])
def start_application():
    # Create a new application
    application = LoanApplication()
    application_id = application.save()
    
    # Store application ID in session
    session['application_id'] = application_id
    
    return redirect(url_for('main.application_process'))

@main.route('/application')
def application_process():
    application_id = session.get('application_id')
    if not application_id:
        return redirect(url_for('main.index'))
    
    application = LoanApplication.load(application_id)
    if not application:
        return redirect(url_for('main.index'))
    
    # Add facial verification step if not completed
    if not application.facial_verification:
        return redirect(url_for('main.face_verification_page'))
    
    # Calculate progress based on current step
    step_progress = {
        'personal_info': 25,
        'financial_info': 50,
        'document_upload': 75,
        'review': 100
    }
    
    # Set default step if not set
    if not application.current_step:
        application.current_step = 'personal_info'
        application.progress = step_progress['personal_info']
        application.save()
    
    # Update progress
    application.progress = step_progress.get(application.current_step, 0)
    application.save()
    
    # If personal info is already provided, skip to next step
    if application.current_step == 'personal_info' and application.full_name:
        application.current_step = 'financial_info'
        application.progress = step_progress['financial_info']
        application.save()
    
    return render_template('application.html', application=application)

@main.route('/api/update_step', methods=['POST'])
def update_step():
    """Update application step and data."""
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    step = data.get('step')
    
    if not step:
        return jsonify({"error": "Missing step"}), 400
    
    try:
        # Update the step
        application.current_step = step
        
        # Calculate progress based on step
        step_progress = {
            'personal_info': 25,
            'financial_info': 50,
            'document_upload': 75,
            'review': 100
        }
        application.progress = step_progress.get(step, 0)
        
        # Save changes
        application.save()
        
        return jsonify({
            "success": True,
            "message": f"Step updated to {step}",
            "progress": application.progress
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/save_response', methods=['POST'])
def save_response():
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    data = request.json
    field = data.get('field')
    value = data.get('value')
    
    if field and value is not None:
        setattr(application, field, value)
        application.save()
    
    next_step = data.get('next_step')
    if next_step:
        application.current_step = next_step
        application.save()
    
    return jsonify({"success": True})

@main.route('/api/upload_video', methods=['POST'])
def upload_video():
    """Handle video upload and processing."""
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check if the file is a webm video
    if not file.filename.endswith('.webm'):
        return jsonify({"error": "Invalid file type. Only .webm files are allowed"}), 400
    
    try:
        # Save video file
        filename = secure_filename(f"{application_id}_{int(time.time())}.webm")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update the application with the video path
        field = request.form.get('field')
        if field:
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
            application.save()
        
        # Return success
        return jsonify({
            "success": True,
            "message": "Video uploaded successfully",
            "video_url": url_for('static', filename=f'uploads/{filename}')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/upload_document', methods=['POST'])
def upload_document():
    """Handle document upload."""
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
    
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not doc_type:
        return jsonify({"error": "No document type specified"}), 400
    
    try:
        # Save document file
        filename = secure_filename(f"{application_id}_{doc_type}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update application with document path
        setattr(application, doc_type, filename)
        application.save()
        
        return jsonify({
            "success": True,
            "message": "Document uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/process_application', methods=['POST'])
def process_application():
    """Process the loan application and determine approval status."""
    application_id = session.get('application_id')
    if not application_id:
        return jsonify({"error": "No active application"}), 400
    
    application = LoanApplication.load(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    try:
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
        
        if has_all_docs and has_personal_info and has_financial_info:
            # For demo purposes, approve if all documents are present
            application.status = 'approved'
            application.save()
            return jsonify({
                "success": True,
                "status": "approved",
                "message": "Congratulations! Your loan application has been approved."
            })
        else:
            application.status = 'rejected'
            application.save()
            missing_items = []
            if not has_personal_info:
                missing_items.append("personal information")
            if not has_financial_info:
                missing_items.append("financial information")
            if not has_all_docs:
                missing_items.append("documents")
            
            return jsonify({
                "success": True,
                "status": "rejected",
                "message": f"Sorry, your loan application has been rejected. Please ensure all required {', '.join(missing_items)} are provided."
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/result')
def result():
    application_id = session.get('application_id')
    if not application_id:
        return redirect(url_for('main.index'))
    
    application = LoanApplication.load(application_id)
    if not application or application.status != "processed":
        return redirect(url_for('main.application_process'))
    
    return render_template('result.html', application=application)

@main.route('/face_verification')
def face_verification_page():
    """Render the facial verification page."""
    application_id = session.get('application_id')
    if not application_id:
        return redirect(url_for('main.index'))
    
    application = LoanApplication.load(application_id)
    if not application:
        return redirect(url_for('main.index'))
    
    # If face is already verified, redirect to application
    if application.facial_verification:
        return redirect(url_for('main.application_process'))
    
    return render_template('face_verification.html', user_id=application_id)