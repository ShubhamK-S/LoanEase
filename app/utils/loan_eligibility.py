def calculate_eligibility(application):
    """
    Rule-based system to determine loan eligibility
    Returns a tuple of (decision, reason)
    """
    # Basic eligibility rules
    min_income = 20000  # Minimum monthly income
    max_loan_multiplier = 36  # Max loan amount = monthly income × multiplier
    
    if not application.facial_verification:
        return "rejected", "Failed facial verification"
    
    if not application.documents.get("id_proof") or not application.documents.get("income_proof"):
        return "more_info", "Missing required documents"
    
    # Income check
    if application.monthly_income < min_income:
        return "rejected", f"Income below minimum requirement of ₹{min_income}"
    
    # Calculate maximum eligible loan amount
    max_eligible_amount = application.monthly_income * max_loan_multiplier
    
    if application.loan_amount > max_eligible_amount:
        return "rejected", f"Requested loan amount exceeds maximum eligible amount of ₹{max_eligible_amount}"
    
    # Employment type factors
    if application.employment_type.lower() == "self-employed":
        # Self-employed applicants need higher income verification
        if application.monthly_income < 30000:
            return "rejected", "Self-employed applicants require minimum income of ₹30,000"
    
    # Loan purpose check - basic filtering
    risky_purposes = ["gambling", "investment", "trading", "cryptocurrency"]
    if any(purpose in application.loan_purpose.lower() for purpose in risky_purposes):
        return "rejected", "Loan purpose not eligible for financing"
    
    # If all checks pass
    return "approved", "Congratulations! Your loan application has been approved."