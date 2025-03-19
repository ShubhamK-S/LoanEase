// Global variables for video recording
let mediaRecorder;
let recordedChunks = [];
let stream;
let currentField;
let nextStep;

function initializeVideoRecording(field, next) {
    currentField = field;
    nextStep = next;
    
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    const userVideo = document.getElementById('user-video');
    
    // Reset previous recording
    recordedChunks = [];
    
    // Enable start button, disable stop button
    startButton.disabled = false;
    stopButton.disabled = true;
    
    // Set up button event listeners
    startButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    
    // Request camera access
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(videoStream => {
            stream = videoStream;
            userVideo.srcObject = stream;
        })
        .catch(error => {
            console.error('Error accessing camera:', error);
            alert('Unable to access camera. Please check your permissions.');
        });
}

function startRecording() {
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    
    // Disable start button, enable stop button
    startButton.disabled = true;
    stopButton.disabled = false;
    
    // Start recording
    mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = function(event) {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };
    
    mediaRecorder.onstop = function() {
        // Create blob from recorded chunks
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        uploadVideo(blob);
    };
    
    mediaRecorder.start();
    
    // Auto-stop after 30 seconds
    setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
            stopRecording();
        }
    }, 30000);
}

function stopRecording() {
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    
    // Disable stop button
    stopButton.disabled = true;
    
    // Stop recording
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    // Stop all tracks
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

function uploadVideo(blob) {
    const formData = new FormData();
    formData.append('video', blob, 'response.webm');
    formData.append('field', currentField);
    formData.append('next_step', nextStep);
    
    fetch('/api/upload_video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI to reflect new step
            document.getElementById('current-step').value = data.current_step;
            updateProgressVisualization(data.current_step);
            initializeApplicationStep(data.current_step);
        } else {
            console.error('Failed to upload video:', data.error);
        }
    })
    .catch(error => {
        console.error('Error uploading video:', error);
    });
}