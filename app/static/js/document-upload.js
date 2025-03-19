// Global variables for document upload
let documentType = 'id_proof';
let documentsUploaded = 0;

function initializeDocumentUpload() {
    const captureButton = document.getElementById('capture-document');
    const uploadButton = document.getElementById('upload-document');
    const documentInput = document.getElementById('document-input');
    const documentPreview = document.getElementById('document-image-preview');
    
    // Reset state
    documentType = documentsUploaded === 0 ? 'id_proof' : 'income_proof';
    document.getElementById('document-type').value = documentType;
    
    // Set up button event listeners
    captureButton.addEventListener('click', () => {
        documentInput.click();
    });
    
    documentInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            // Enable upload button
            uploadButton.disabled = false;
            
            // Show preview
            const file = event.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                documentPreview.src = e.target.result;
                documentPreview.style.display = 'block';
            };
            
            reader.readAsDataURL(file);
        }
    });
    
    // Setup form submission
    document.getElementById('document-upload-form').addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(this);
        
        fetch('/api/upload_document', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                documentsUploaded++;
                
                if (documentsUploaded < 2) {
                    // Reset for next document
                    documentType = 'income_proof';
                    document.getElementById('document-type').value = documentType;
                    documentPreview.style.display = 'none';
                    documentInput.value = '';
                    uploadButton.disabled = true;
                    
                    // Alert user about next document
                    alert('ID proof uploaded successfully. Please upload your income proof document next.');
                } else {
                    // Both documents uploaded, move to processing
                    document.getElementById('current-step').value = 'processing';
                    updateProgressVisualization('processing');
                    initializeApplicationStep('processing');
                }
            } else {
                console.error('Failed to upload document:', data.error);
            }
        })
        .catch(error => {
            console.error('Error uploading document:', error);
        });
    });
}