document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const transcriptionText = document.getElementById('transcriptionText');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const timerDisplay = document.getElementById('timerDisplay');
    
    // Tab elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Report content elements
    const entitiesContent = document.getElementById('entitiesContent');
    const soapContent = document.getElementById('soapContent');
    const evidenceContent = document.getElementById('evidenceContent');
    const fullReportContent = document.getElementById('fullReportContent');
    
    // State variables
    let audioBlob = null;
    let transcription = '';
    let reportData = null;
    
    // Initialize tabs
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Event Listeners
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    analyzeBtn.addEventListener('click', analyzeConversation);
    downloadBtn.addEventListener('click', downloadReport);
    
    // Start recording function
    function startRecording() {
        // Implemented in recorder.js
        startAudioRecording();
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingIndicator.classList.remove('hidden');
        startTimer();
    }
    
    // Stop recording function
    function stopRecording() {
        // Implemented in recorder.js
        stopAudioRecording();
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        recordingIndicator.classList.add('hidden');
        stopTimer();
        
        // Enable analyze button
        analyzeBtn.disabled = false;
    }
    
    // Timer functions
    let timerInterval;
    let seconds = 0;
    
    function startTimer() {
        seconds = 0;
        updateTimerDisplay();
        timerInterval = setInterval(() => {
            seconds++;
            updateTimerDisplay();
        }, 1000);
    }
    
    function stopTimer() {
        clearInterval(timerInterval);
    }
    
    function updateTimerDisplay() {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `${mins}:${secs}`;
    }
    
    // Analyze conversation function
    async function analyzeConversation() {
        if (!transcriptionText.value.trim()) {
            alert('Please record and transcribe a conversation first.');
            return;
        }
        
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        
        try {
            // Simulate API calls (replace with actual API calls to your backend)
            // 1. Extract medical entities
            const entities = await extractMedicalEntities(transcriptionText.value);
            
            // 2. Generate SOAP note
            const soapNote = await generateSOAPNote(transcriptionText.value, entities);
            
            // 3. Get evidence-based recommendations
            const evidence = await getEvidenceRecommendations(entities);
            
            // 4. Generate full report
            const fullReport = await generateFullReport(transcriptionText.value, entities, soapNote, evidence);
            
            // Store report data
            reportData = {
                entities,
                soapNote,
                evidence,
                fullReport
            };
            
            // Update UI with the results
            displayEntities(entities);
            displaySOAPNote(soapNote);
            displayEvidence(evidence);
            displayFullReport(fullReport);
            
            // Enable download button
            downloadBtn.disabled = false;
            
        } catch (error) {
            console.error('Error analyzing conversation:', error);
            alert('An error occurred while analyzing the conversation. Please try again.');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Conversation';
        }
    }
    
    // Display medical entities
    function displayEntities(entities) {
        let html = `
            <div class="entity-card symptoms">
                <div class="entity-type">
                    <i class="fas fa-thermometer-half"></i> Symptoms
                </div>
                <div class="entity-list">
                    ${entities.symptoms.length > 0 ? 
                        entities.symptoms.map(s => `<span class="entity-item">${s}</span>`).join('') : 
                        '<span class="no-entities">No symptoms identified</span>'}
                </div>
            </div>
            
            <div class="entity-card conditions">
                <div class="entity-type">
                    <i class="fas fa-diagnoses"></i> Conditions
                </div>
                <div class="entity-list">
                    ${entities.conditions.length > 0 ? 
                        entities.conditions.map(c => `<span class="entity-item">${c}</span>`).join('') : 
                        '<span class="no-entities">No conditions identified</span>'}
                </div>
            </div>
            
            <div class="entity-card medications">
                <div class="entity-type">
                    <i class="fas fa-pills"></i> Medications
                </div>
                <div class="entity-list">
                    ${entities.medications.length > 0 ? 
                        entities.medications.map(m => `<span class="entity-item">${m}</span>`).join('') : 
                        '<span class="no-entities">No medications identified</span>'}
                </div>
            </div>
        `;
        
        entitiesContent.innerHTML = html;
    }
    
    // Display SOAP note
    function displaySOAPNote(soapNote) {
        // Format the SOAP note with proper line breaks and sections
        const formattedNote = soapNote.replace(/\n/g, '<br>')
                                    .replace(/\[(.*?)\]/g, '<strong>$1</strong>');
        
        soapContent.innerHTML = `<div class="soap-note">${formattedNote}</div>`;
    }
    
    // Display evidence
    function displayEvidence(evidence) {
        // Parse evidence and format for display
        const evidenceItems = evidence.split('\n\n').filter(item => item.trim());
        
        let html = '';
        evidenceItems.forEach((item, index) => {
            const parts = item.split('\n');
            if (parts.length >= 2) {
                const title = parts[0].replace(/^\d+\.\s*/, '');
                const content = parts.slice(1).join('<br>');
                
                html += `
                    <div class="evidence-item">
                        <div class="evidence-title">${index + 1}. ${title}</div>
                        <div class="evidence-content">${content}</div>
                    </div>
                `;
            }
        });
        
        evidenceContent.innerHTML = html || '<p>No evidence recommendations available.</p>';
    }
    
    // Display full report
    function displayFullReport(fullReport) {
        // Format the report with proper sections and styling
        const formattedReport = fullReport
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*?):/gm, '<h3>$1:</h3>')
            .replace(/•/g, '<li>')
            .replace(/(<h3>.*?<\/h3>)/g, '</div><div class="report-section">$1');
        
        fullReportContent.innerHTML = `<div class="full-report">${formattedReport}</div>`;
    }
    
    // Download report function
    function downloadReport() {
        if (!reportData || !reportData.fullReport) {
            alert('No report available to download.');
            return;
        }
        
        // Create a blob with the report content
        const blob = new Blob([reportData.fullReport], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        // Create a download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `medical_report_${new Date().toISOString().slice(0, 10)}.txt`;
        
        // Trigger the download
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // Mock API functions (replace with actual API calls to your backend)
    async function extractMedicalEntities(text) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // This would be replaced with actual API call to your NER endpoint
        // For now, we'll simulate some entities
        return {
            symptoms: ['headache', 'dizziness'],
            conditions: ['hypertension'],
            medications: ['metoprolol']
        };
    }
    
    async function generateSOAPNote(text, entities) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // This would be replaced with actual API call to your SOAP generator
        return `[Subjective]
Patient reports persistent headache for the past 3 days, rated 6/10 in severity. Also complains of occasional dizziness, especially when standing up quickly. Patient has known history of hypertension and is currently taking metoprolol.

[Objective]
BP: 145/90 mmHg, Pulse: 78 bpm, Temp: 98.6°F. No focal neurological deficits noted. Fundoscopic exam normal.

[Assessment]
1. Persistent headache - likely tension-type, but rule out secondary causes
2. Controlled hypertension
3. Orthostatic dizziness - may need medication adjustment

[Plan]
1. Recommend head CT if headache persists or worsens
2. Continue current antihypertensive regimen
3. Advise slow position changes
4. Follow up in 2 weeks`;
    }
    
    async function getEvidenceRecommendations(entities) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        // This would be replaced with actual API call to your evidence synthesis endpoint
        return `1. Title: Management of Hypertension in Adults
   Summary: Current guidelines recommend target BP <130/80 for most adults with hypertension. Lifestyle modifications and first-line antihypertensives like metoprolol are effective.

2. Title: Evaluation of Chronic Headache
   Summary: For patients with persistent headache, consider secondary causes if red flags present. Neuroimaging is recommended for new or changing headache patterns.

3. Title: Orthostatic Hypotension Management
   Summary: Medication review is essential for patients with orthostatic symptoms. Dose adjustment or timing changes may reduce dizziness episodes.`;
    }
    
    async function generateFullReport(text, entities, soapNote, evidence) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // This would be replaced with actual API call to your report generator
        const reportDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `PATIENT MEDICAL REPORT
Generated on: ${reportDate}
==========================================

PATIENT SUMMARY:
The patient presents with complaints of persistent headache and occasional dizziness. They have a known history of hypertension and are currently prescribed metoprolol.

IDENTIFIED MEDICAL ENTITIES:
• Symptoms: headache, dizziness
• Conditions: hypertension
• Medications: metoprolol

CLINICAL ASSESSMENT (SOAP FORMAT):
${soapNote}

EVIDENCE-BASED RECOMMENDATIONS:
${evidence}

PATIENT-FRIENDLY SUMMARY:
• Your headaches and dizziness may be related to your blood pressure
• Continue taking your metoprolol as prescribed
• Get up slowly from sitting or lying down to prevent dizziness
• Contact your doctor if headaches worsen or you develop new symptoms
• Schedule a follow-up appointment in 2 weeks`;
    }
    
    // Function to receive transcription from recorder.js
    window.receiveTranscription = function(text) {
        transcriptionText.value = text;
        transcription = text;
    };
});