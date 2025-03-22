import google.generativeai as genai
import json

def load_entities_from_json(json_path):
    """Load medical entities from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return (data['symptoms'], data['conditions'], data['medications'])
    except Exception as e:
        print(f"Error loading entities: {e}")
        return ([], [], [])

def generate_soap_with_gemini(transcription_path, entities_json_path):
    """Generate SOAP note using transcription file and entities JSON"""
    try:
        # Read transcription text
        with open(transcription_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        # Load entities from JSON
        symptoms, conditions, medications = load_entities_from_json(entities_json_path)
        
        # Configure Google AI
        genai.configure(api_key="AIzaSyDooyEJKTTh6Dwj7ntEDpBzlf50rzdEk-M")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate prompt
        prompt = f"""
        Generate structured SOAP note from:
        Patient Statement: "{original_text}"
        Identified Symptoms: {symptoms}
        Medical Conditions: {conditions}
        Current Medications: {medications}
        
        Format:
        [SOAP Note]
        Subjective (S): <patient-reported info>
        Objective (O): <clinical findings>
        Assessment (A): <diagnosis analysis>
        Plan (P): <treatment plan>
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating SOAP note: {e}"

# File paths (use raw strings for Windows paths)
transcription_file = r"C:/Users/MD.ZAID SHAIKH/Documents/transcription.txt"
entities_json = r"C:/Users/MD.ZAID SHAIKH/Documents/AI_Medical_Assistant/backend/models/services/medical_entities.json"

# Generate and print SOAP note
print(generate_soap_with_gemini(transcription_file, entities_json))