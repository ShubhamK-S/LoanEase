class FaceVerification {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.userId = null;
    }

    async initialize(videoElementId, canvasElementId, userId) {
        this.video = document.getElementById(videoElementId);
        this.canvas = document.getElementById(canvasElementId);
        this.userId = userId;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.video.srcObject = this.stream;
            console.log("Webcam initialized successfully");
        } catch (err) {
            console.error('Error accessing webcam:', err);
            throw new Error('Failed to access webcam');
        }
    }

    async captureImage() {
        const context = this.canvas.getContext('2d');
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        return new Promise((resolve) => {
            this.canvas.toBlob(resolve, 'image/jpeg', 0.8);
        });
    }

    async registerFace() {
        try {
            console.log("Starting face registration...");
            const imageBlob = await this.captureImage();
            const formData = new FormData();
            formData.append('image', imageBlob, 'face.jpg');
            formData.append('user_id', this.userId);

            console.log("Sending registration request...");
            const response = await fetch('/api/register_face', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Registration response:", result);
            return result;
        } catch (err) {
            console.error('Error registering face:', err);
            throw err;
        }
    }

    async verifyFace() {
        try {
            console.log("Starting face verification...");
            const imageBlob = await this.captureImage();
            const formData = new FormData();
            formData.append('image', imageBlob, 'face.jpg');
            formData.append('user_id', this.userId);

            console.log("Sending verification request...");
            const response = await fetch('/api/verify_face', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Verification response:", result);
            return result;
        } catch (err) {
            console.error('Error verifying face:', err);
            throw err;
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
            console.log("Webcam stopped");
        }
    }
}

// Example usage:
/*
const faceVerification = new FaceVerification();

// Initialize
await faceVerification.initialize('videoElement', 'canvasElement', 'user123');

// Register face
const registerResult = await faceVerification.registerFace();
console.log(registerResult);

// Verify face
const verifyResult = await faceVerification.verifyFace();
console.log(verifyResult);

// Stop when done
faceVerification.stop();
*/ 