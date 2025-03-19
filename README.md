# LoanEase - AI-Powered Loan Application System

LoanEase is a modern, AI-powered loan application system that streamlines the loan application process through facial verification, video responses, and automated document processing. Built with Flask and Python, it offers a secure and user-friendly interface for loan applications.

## Features

- **Facial Verification**: Secure identity verification using facial recognition
- **Video Responses**: Record video responses for personal and financial information
- **Document Upload**: Secure document upload for PAN card, ID proof, and income proof
- **Progress Tracking**: Real-time progress tracking throughout the application process
- **AI-Powered Processing**: Automated application processing and decision making
- **Responsive Design**: Mobile-friendly interface built with Bootstrap
- **Secure Authentication**: User authentication and session management
- **CSRF Protection**: Built-in security measures for form submissions

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: JSON-based file storage
- **Authentication**: Flask-Login
- **Security**: Flask-WTF (CSRF protection)
- **Video Processing**: MediaRecorder API

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser with camera access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/loanease.git
cd loanease
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

5. Create required directories:
```bash
mkdir -p app/static/videos app/static/documents
```

## Running the Application

1. Start the Flask development server:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
loanease/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── videos/
│   │   └── documents/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── application.html
│       └── steps/
│           ├── personal_info.html
│           ├── financial_info.html
│           ├── document_upload.html
│           └── review.html
├── config.py
├── requirements.txt
├── run.py
└── .env
```

## Application Flow

1. User registers/logs in
2. Starts a new loan application
3. Completes facial verification
4. Provides personal information with video response
5. Provides financial information with video response
6. Uploads required documents
7. Reviews application details
8. Submits application for processing
9. Receives AI-powered decision

## Security Features

- CSRF protection for all forms
- Secure file upload handling
- Session-based authentication
- Environment variable configuration
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework and its extensions
- Bootstrap for the UI components
- MediaRecorder API for video recording
- All contributors and maintainers

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 