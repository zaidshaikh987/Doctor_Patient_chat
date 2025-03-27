// Audio recording functionality
let mediaRecorder;
let audioChunks = [];
let audioContext;
let analyser;
let canvasCtx;
let animationId;

// Initialize audio visualization
function initVisualizer() {
    const canvas = document.getElementById('visualizer');
    canvasCtx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

// Start audio recording
async function startAudioRecording() {
    try {
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Set up audio context and analyser for visualization
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;
        
        // Start visualization
        initVisualizer();
        visualize();
        
        // Set up media recorder
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            // Stop visualization
            cancelAnimationFrame(animationId);
            
            // Create audio blob
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            
            // Send to backend for transcription (simulated here)
            simulateTranscription(audioBlob);
            
            // Clean up
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Could not start recording. Please ensure microphone access is granted.');
    }
}

// Stop audio recording
function stopAudioRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}

// Audio visualization
function visualize() {
    const canvas = document.getElementById('visualizer');
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;
    
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    function draw() {
        animationId = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        
        canvasCtx.fillStyle = 'rgb(236, 240, 241)';
        canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
        
        const barWidth = (WIDTH / bufferLength) * 2.5;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * HEIGHT;
            
            canvasCtx.fillStyle = `rgb(52, 152, 219)`;
            canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    draw();
}

// Simulate transcription (replace with actual API call to your backend)
function simulateTranscription(audioBlob) {
    // Show loading state
    const transcriptionText = document.getElementById('transcriptionText');
    transcriptionText.value = "Processing audio...";
    
    // Simulate API call delay
    setTimeout(() => {
        // This would be replaced with actual API call to your transcription endpoint
        const sampleTranscription = `Doctor: How have you been feeling since your last visit?
Patient: Not great, I've had this persistent headache for about 3 days now.
Doctor: On a scale of 1 to 10, how would you rate the pain?
Patient: About a 6. I also feel dizzy sometimes when I stand up.
Doctor: Are you still taking your metoprolol for hypertension?
Patient: Yes, I take it every morning.`;
        
        // Update UI with transcription
        transcriptionText.value = sampleTranscription;
        
        // Call the global function to notify the main app
        if (window.receiveTranscription) {
            window.receiveTranscription(sampleTranscription);
        }
    }, 3000);
}

// Expose functions to global scope
window.startAudioRecording = startAudioRecording;
window.stopAudioRecording = stopAudioRecording;