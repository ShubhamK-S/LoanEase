import cv2
import os
import time
import requests
from pathlib import Path
from flask import current_app

class FaceVerifier:
    def __init__(self):
        # Face++ API Credentials
        self.API_KEY = current_app.config['FACEPP_API_KEY']
        self.API_SECRET = current_app.config['FACEPP_API_SECRET']
        self.API_URL = "https://api-us.faceplusplus.com/facepp/v3"
        
        # Face++ API Endpoints
        self.DETECT_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
        self.COMPARE_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"
        
        # Setup directories
        self.BASE_DIR = Path(__file__).parent
        self.IMAGE_DIR = self.BASE_DIR / "live_images"
        self.IMAGE_DIR.mkdir(exist_ok=True)
        
        # Create stored faces directory
        self.STORED_FACES_DIR = self.BASE_DIR / "stored_faces"
        self.STORED_FACES_DIR.mkdir(exist_ok=True)
        
        print(f"Initialized FaceVerifier with directories:")
        print(f"Image Directory: {self.IMAGE_DIR}")
        print(f"Stored Faces Directory: {self.STORED_FACES_DIR}")

    def detect_face(self, image_data):
        """Detect if a face exists in the given image data."""
        try:
            response = requests.post(
                self.DETECT_URL,
                data={"api_key": self.API_KEY, "api_secret": self.API_SECRET},
                files={"image_file": ("image.jpg", image_data, "image/jpeg")},
            )
            
            result = response.json()
            if "faces" in result and len(result["faces"]) > 0:
                print("✅ Face detected in image")
                return True
            else:
                print("❌ No face detected in image")
                return False
        except Exception as e:
            print(f"Error in face detection: {str(e)}")
            return False

    def compare_faces(self, image1_path, image2_data):
        """Compare two face images and return confidence score."""
        try:
            with open(image1_path, "rb") as img1:
                response = requests.post(
                    self.COMPARE_URL,
                    data={"api_key": self.API_KEY, "api_secret": self.API_SECRET},
                    files={
                        "image_file1": ("image1.jpg", img1.read(), "image/jpeg"),
                        "image_file2": ("image2.jpg", image2_data, "image/jpeg")
                    },
                )
            
            result = response.json()
            if "confidence" in result:
                return result["confidence"]
            return 0
        except Exception as e:
            print(f"Error in face comparison: {str(e)}")
            return 0

    def save_image(self, image_data, filename):
        """Save image data to file."""
        try:
            filepath = self.IMAGE_DIR / filename
            with open(filepath, "wb") as f:
                f.write(image_data)
            print(f"📸 Image saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return None

    def verify_face(self, image_data):
        """Verify face in the image using Face++ API"""
        try:
            # Detect face in the image
            detect_response = requests.post(
                f"{self.API_URL}/detect",
                data={
                    "api_key": self.API_KEY,
                    "api_secret": self.API_SECRET,
                    "image_base64": image_data,
                    "return_landmark": 1
                }
            )
            
            if detect_response.status_code != 200:
                return False, "Failed to detect face in the image"
            
            detect_result = detect_response.json()
            
            if not detect_result.get('faces'):
                return False, "No face detected in the image"
            
            # Compare with stored face
            compare_response = requests.post(
                f"{self.API_URL}/compare",
                data={
                    "api_key": self.API_KEY,
                    "api_secret": self.API_SECRET,
                    "face_token1": detect_result['faces'][0]['face_token'],
                    "face_token2": self.get_stored_face_token()
                }
            )
            
            if compare_response.status_code != 200:
                return False, "Failed to compare faces"
            
            compare_result = compare_response.json()
            
            # Check if confidence is above threshold
            if compare_result.get('confidence', 0) > 80:
                return True, "Face verification successful"
            else:
                return False, "Face verification failed - confidence too low"
                
        except Exception as e:
            return False, f"Error during face verification: {str(e)}"

    def get_stored_face_token(self):
        """Get the stored face token for comparison"""
        # TODO: Implement face token storage and retrieval
        return "stored_face_token"

    def verify_identity(self, live_image_data, user_id):
        """Verify user identity using stored face image."""
        try:
            # Save live image
            live_image_path = self.save_image(live_image_data, f"live_{int(time.time())}.jpg")
            if not live_image_path:
                return False, "Failed to save live image"
            
            # Get stored face image path
            stored_image_path = self.STORED_FACES_DIR / f"{user_id}.jpg"
            if not stored_image_path.exists():
                return False, "No stored face image found for this user"
            
            # Detect face in live image
            if not self.detect_face(live_image_data):
                return False, "No face detected in the image"
            
            # Compare faces
            confidence = self.compare_faces(str(stored_image_path), live_image_data)
            
            # Clean up live image
            os.remove(live_image_path)
            
            if confidence > 80:
                return True, f"Identity verified with {confidence:.2f}% confidence"
            else:
                return False, f"Identity verification failed. Confidence: {confidence:.2f}%"
        except Exception as e:
            print(f"Error in verify_identity: {str(e)}")
            return False, f"Error during verification: {str(e)}"

    def store_face(self, image_data, user_id):
        """Store a user's face image for future verification."""
        try:
            if not self.detect_face(image_data):
                return False, "No face detected in the image"
            
            filepath = self.STORED_FACES_DIR / f"{user_id}.jpg"
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            print(f"✅ Face image stored successfully at: {filepath}")
            return True, "Face image stored successfully"
        except Exception as e:
            print(f"Error in store_face: {str(e)}")
            return False, f"Error storing face image: {str(e)}" 