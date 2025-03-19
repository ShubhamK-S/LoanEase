import os
import google.generativeai as genai
from PIL import Image
from flask import current_app

def setup_gemini():
    genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
    return genai.GenerativeModel('gemini-pro-vision')

def extract_document_info(document_path, document_type):
    """
    Extract information from uploaded documents using Google Gemini API
    """
    try:
        model = setup_gemini()
        
        # Open the image
        img = Image.open(document_path)
        
        # Prepare the prompt based on document type
        if document_type == "id_proof":
            prompt = """
            Extract the following information from this ID document (Aadhaar/PAN):
            1. Full Name
            2. Date of Birth (if available)
            3. ID Number
            Format the response as a JSON object with keys: name, dob, id_number
            """
        elif document_type == "income_proof":
            prompt = """
            Extract the following information from this income document:
            1. Monthly/Annual Income
            2. Employment Type (Salaried/Self-employed)
            3. Company Name (if available)
            Format the response as a JSON object with keys: income, employment_type, company
            """
        else:
            return {"error": "Invalid document type"}
        
        response = model.generate_content([prompt, img])
        
        # Extract JSON from response
        response_text = response.text
        
        # Simple parsing to extract JSON part - in a production app, use better parsing
        import json
        import re
        
        # Find JSON content between braces
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                return result
            except json.JSONDecodeError:
                return {"error": "Failed to parse document information"}
        else:
            # Fallback to structured extraction if JSON not found
            result = {}
            if document_type == "id_proof":
                # Extract basic info with simple patterns
                name_match = re.search(r'name[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if name_match:
                    result["name"] = name_match.group(1).strip()
                dob_match = re.search(r'(date of birth|dob)[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if dob_match:
                    result["dob"] = dob_match.group(2).strip()
                id_match = re.search(r'(id number|aadhaar|pan)[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if id_match:
                    result["id_number"] = id_match.group(2).strip()
            elif document_type == "income_proof":
                income_match = re.search(r'income[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if income_match:
                    result["income"] = income_match.group(1).strip()
                emp_match = re.search(r'employment type[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if emp_match:
                    result["employment_type"] = emp_match.group(1).strip()
                company_match = re.search(r'company[:\s]+([^\n]+)', response_text, re.IGNORECASE)
                if company_match:
                    result["company"] = company_match.group(1).strip()
            
            return result
        
    except Exception as e:
        return {"error": str(e)}