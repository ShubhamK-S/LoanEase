import cv2
import os
import numpy as np
import mediapipe as mp
from flask import current_app

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def detect_face(image_path):
    """
    Detect faces in an image using MediaPipe
    Returns True if exactly one face is detected, False otherwise
    """
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image_rgb)
        
        # Check if exactly one face is detected
        if results.detections and len(results.detections) == 1:
            return True
        return False

def save_face_embedding(image_path, application_id):
    """
    Simple prototype for saving facial features
    In a real app, you'd use a proper face recognition library
    """
    # For prototype, we'll just verify a face exists and save the detection result
    has_face = detect_face(image_path)
    
    # Save result to application record
    result_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{application_id}_face_verified.txt")
    with open(result_path, 'w') as f:
        f.write(str(has_face))
    
    return has_face

def verify_face_consistency(image_path, application_id):
    """
    For prototype, just check if a face was detected previously
    In a real app, you'd compare face embeddings
    """
    # Check if previous verification exists
    previous_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{application_id}_face_verified.txt")
    
    if not os.path.exists(previous_path):
        # First time verification
        return save_face_embedding(image_path, application_id)
    
    # For prototype, just check if current image has a face
    return detect_face(image_path)