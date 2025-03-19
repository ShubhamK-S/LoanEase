// Common JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Handle alert dismissal
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                alert.remove();
            });
        }
    });

    // Get current step from input
    const currentStep = document.getElementById('current-step').value;
    
    // Update progress visualization
    updateProgressVisualization(currentStep);
    
    // Initialize application flow based on current step
    initializeApplicationStep(currentStep);
});

function updateProgressVisualization(step) {
    // Reset all steps
    document.querySelectorAll('.progress-steps li').forEach(item => {
        item.classList.remove('active', 'completed');
    });
    
    // Set active step
    const activeStep = document.querySelector(`.progress-steps li[data-step="${step}"]`);
    if (activeStep) {
        activeStep.classList.add('active');
        
        // Mark previous steps as completed
        let prevElement = activeStep.previousElementSibling;
        while (prevElement) {
            prevElement.classList.add('completed');
            prevElement = prevElement.previousElementSibling;
        }
    }
}

function initializeApplicationStep(step) {
    console.log(`Initializing step: ${step}`);
    
    // Hide all containers
    document.getElementById('user-video-container').classList.add('hidden');
    document.getElementById('document-upload-container').classList.add('hidden');
    
    // Show appropriate container based on step
    switch (step) {
        case 'welcome':
            playBankManagerVideo('welcome.mp4', () => {
                // After welcome video, move to personal info
                updateStepOnServer('personal_info');
            });
            break;
            
        case 'personal_info':
            playBankManagerVideo('ask_name.mp4', () => {
                // After asking name, show video recording
                document.getElementById('user-video-container').classList.remove('hidden');
                initializeVideoRecording('applicant_name', 'financial_info');
            });
            break;
            
        case 'financial_info':
            playBankManagerVideo('ask_income.mp4', () => {
                // After asking about income, show video recording
                document.getElementById('user-video-container').classList.remove('hidden');
                initializeVideoRecording('monthly_income', 'loan_details');
            });
            break;
            
        case 'loan_details':
            playBankManagerVideo('ask_loan_purpose.mp4', () => {
                // After asking about loan purpose, show video recording
                document.getElementById('user-video-container').classList.remove('hidden');
                initializeVideoRecording('loan_purpose', 'document_upload');
            });
            break;
            
        case 'document_upload':
            playBankManagerVideo('ask_documents.mp4', () => {
                // After asking for documents, show document upload
                document.getElementById('document-upload-container').classList.remove('hidden');
                initializeDocumentUpload();
            });
            break;
            
        case 'processing':
            playBankManagerVideo('processing.mp4', () => {
                // After processing video, submit application
                processApplication();
            });
            break;
            
        case 'decision':
            const applicationId = document.getElementById('application-id').value;
            // Redirect to result page
            window.location.href = `/result`;
            break;
            
        default:
            console.error('Unknown step:', step);
            break;
    }
}

function playBankManagerVideo(videoName, onEndCallback) {
    const video = document.getElementById('bank-manager-video');
    video.src = `/static/videos/${videoName}`;
    
    video.onended = function() {
        if (onEndCallback) {
            onEndCallback();
        }
    };
    
    video.play().catch(error => {
        console.error('Error playing video:', error);
        // Fallback for browsers that don't allow autoplay
        const playButton = document.createElement('button');
        playButton.textContent = 'Play Video';
        playButton.className = 'btn';
        playButton.onclick = function() {
            video.play();
            playButton.remove();
        };
        document.getElementById('bank-manager-container').appendChild(playButton);
    });
}

function updateStepOnServer(step) {
    fetch('/api/update_step', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ step: step }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI to reflect new step
            document.getElementById('current-step').value = data.current_step;
            updateProgressVisualization(data.current_step);
            initializeApplicationStep(data.current_step);
        } else {
            console.error('Failed to update step:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating step:', error);
    });
}

function processApplication() {
    fetch('/api/process_application', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Move to decision step after processing
            updateStepOnServer('decision');
        } else {
            console.error('Failed to process application:', data.error);
        }
    })
    .catch(error => {
        console.error('Error processing application:', error);
    });
}