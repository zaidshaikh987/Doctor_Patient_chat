# app.py
import streamlit as st
import os
import json
from audio_integrate import record_audio, transcribe_audio
from medical_entity import extract_medical_entities
from soap_generator import generate_soap_with_gemini
from evidence_synthesis import generate_evidence_report

# Configure paths
BASE_DIR = os.path.expanduser("~")
AUDIO_PATH = os.path.join(BASE_DIR, "Documents", "patient_conversation.wav")
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "Documents", "transcription.txt")
ENTITIES_JSON = os.path.join(BASE_DIR, "Documents", "AI_Medical_Assistant", "backend", "models", "services", "medical_entities.json")

def main():
    st.title("AI-Powered Medical Assistant 🏥")
    
    # Initialize session state
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""
    if 'entities' not in st.session_state:
        st.session_state.entities = {"symptoms": [], "conditions": [], "medications": []}
    
    # Navigation
    tabs = ["Audio Recording", "Clinical Analysis", "Research Synthesis"]
    current_tab = st.sidebar.radio("Navigation", tabs)
    
    # Audio Recording Tab
    if current_tab == "Audio Recording":
        st.header("Patient Conversation Recording 🎙️")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Recording (15s)"):
                record_audio(duration=15)
                st.success("Audio recorded successfully!")
        
        with col2:
            if st.button("Transcribe Audio"):
                try:
                    transcribe_audio()
                    with open(TRANSCRIPT_PATH, 'r') as f:
                        st.session_state.transcription = f.read()
                    st.success("Transcription completed!")
                except Exception as e:
                    st.error(f"Transcription error: {str(e)}")
        
        if st.session_state.transcription:
            st.subheader("Transcript")
            st.text_area("Conversation", st.session_state.transcription, height=200)
    
    # Clinical Analysis Tab
    elif current_tab == "Clinical Analysis":
        st.header("Clinical Analysis 🤖")
    
        # Entity Extraction Section
        if st.button("Extract Medical Entities"):
            try:
                with open(TRANSCRIPT_PATH, 'r') as f:
                    text = f.read()
                symptoms, conditions, medications = extract_medical_entities(text)
                
                # Store in session state
                st.session_state.entities = {
                    "symptoms": symptoms,
                    "conditions": conditions,
                    "medications": medications
                }
                
                # Save to JSON
                with open(ENTITIES_JSON, 'w') as f:
                    json.dump(st.session_state.entities, f)
                
                st.success("✅ Medical entities extracted successfully!")
            
            except Exception as e:
                st.error(f"🚨 Extraction error: {str(e)}")
    
    # Always show entities if available
    if st.session_state.entities:
        st.subheader("Extracted Medical Entities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Symptoms**")
            if st.session_state.entities["symptoms"]:
                for symptom in st.session_state.entities["symptoms"]:
                    st.write(f"- {symptom}")
            else:
                st.write("No symptoms detected")
        
        with col2:
            st.markdown("**Conditions**")
            if st.session_state.entities["conditions"]:
                for condition in st.session_state.entities["conditions"]:
                    st.write(f"- {condition}")
            else:
                st.write("No conditions detected")
        
        with col3:
            st.markdown("**Medications**")
            if st.session_state.entities["medications"]:
                for med in st.session_state.entities["medications"]:
                    st.write(f"- {med}")
            else:
                st.write("No medications detected")
        
        # Auto-generate SOAP note
        try:
            st.subheader("SOAP Note Generation 📋")
            soap_note = generate_soap_with_gemini(TRANSCRIPT_PATH, ENTITIES_JSON)
            st.markdown(f"""
            ```markdown
            {soap_note}
            """)
        except Exception as e:
            st.error(f"🚨 SOAP generation failed: {str(e)}")
    # Research Synthesis Tab
    elif current_tab == "Research Synthesis":
        st.header("Medical Evidence Synthesis 📚")
        
        if st.button("Fetch Relevant Research"):
            try:
                with st.spinner("Analyzing latest medical research..."):
                    evidence_report = generate_evidence_report(ENTITIES_JSON)
                    st.subheader("Research Summary")
                    st.markdown(evidence_report)
            except Exception as e:
                st.error(f"Research synthesis error: {str(e)}")

if __name__ == "__main__":
    main()