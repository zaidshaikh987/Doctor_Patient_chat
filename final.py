from fastapi import FastAPI
from pydantic import BaseModel
import spacy
import requests
from transformers import pipeline

# Load spaCy NLP model for entity extraction
nlp = spacy.load("en_core_web_sm")

# FastAPI app
app = FastAPI()

# Initialize Hugging Face transformers (optional: for further model fine-tuning)
summarizer = pipeline("summarization")

# Gemini API key and endpoint setup
GEMINI_API_KEY = "AIzaSyBZ-54ew4qLODX2dY_05XaYDVzzbnct70g"
GEMINI_API_URL = "https://api.gemini.com/generate_soap_note"

# Dummy data for doctor-patient conversation
dummy_data = [
    {"role": "doctor", "text": "How are you feeling today?"},
    {"role": "patient", "text": "I've been feeling dizzy, especially when I stand up quickly."},
    {"role": "doctor", "text": "Do you have any other symptoms?"},
    {"role": "patient", "text": "I feel weak and sometimes get headaches."},
]

# Pydantic model for input and output
class MedicalInput(BaseModel):
    conversation: list

class MedicalOutput(BaseModel):
    symptoms: list
    possible_conditions: list
    medications: list
    soap_note: str
    health_risk: str
    research_summary: str
    bias_detection: str

# Function to extract medical entities using spaCy
def extract_medical_entities(conversation):
    text = " ".join([entry['text'] for entry in conversation])
    doc = nlp(text)
    symptoms = []
    conditions = []
    medications = []

    # Dummy entity extraction logic (you can expand this with custom logic for medical terms)
    for ent in doc.ents:
        if ent.label_ == "SYMPTOM":
            symptoms.append(ent.text)
        elif ent.label_ == "DISEASE":
            conditions.append(ent.text)
        # Add more conditions for medications, etc.

    return symptoms, conditions, medications

# Function to generate SOAP notes using Gemini API
def generate_soap_note(symptoms, conditions):
    soap_prompt = f"Generate a SOAP note with symptoms: {symptoms} and conditions: {conditions}."
    
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": soap_prompt
    }
    
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("soap_note", "")
    else:
        return "Error generating SOAP note."

# Function to summarize research from PubMed or any other API
def fetch_medical_research():
    # Placeholder for real API integration with PubMed or similar
    return "Research suggests that dizziness can be caused by dehydration, especially in older adults. Hydration therapy can help alleviate symptoms."

# Function to predict health risks based on data
def predict_health_risks():
    # Placeholder prediction logic (you can use machine learning models here)
    return "72% likelihood of dehydration-related dizziness within the next 6 months."

# Function to detect bias in treatment recommendations
def detect_bias():
    # Placeholder for bias detection logic
    return "Hydration therapy is under-prescribed for women over 50 in the current dataset."

@app.post("/analyze_medical_dialogue", response_model=MedicalOutput)
async def analyze_medical_dialogue(input_data: MedicalInput):
    # Extract medical entities from conversation
    symptoms, conditions, medications = extract_medical_entities(input_data.conversation)

    # Generate SOAP notes using Gemini API
    soap_note = generate_soap_note(symptoms, conditions)

    # Fetch relevant medical research
    research_summary = fetch_medical_research()

    # Predict health risks
    health_risk = predict_health_risks()

    # Detect bias in historical data
    bias_detection = detect_bias()

    # Return structured output
    return MedicalOutput(
        symptoms=symptoms,
        possible_conditions=conditions,
        medications=medications,
        soap_note=soap_note,
        health_risk=health_risk,
        research_summary=research_summary,
        bias_detection=bias_detection
    )

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
