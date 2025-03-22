import json 
import spacy

nlp = spacy.load("en_core_web_sm")  # General-purpose model

def extract_medical_entities(text):
    """Extract medical terms using n-grams and keyword matching."""
    doc = nlp(text.lower())

    # Define lowercase keyword sets
    symptom_keywords = {"dizziness", "palpitations", "fatigue", "nausea", "headache", "insomnia", "chronic pain", "muscle weakness", 
    "joint pain", "fever", "weight loss", "swelling", "cough", "shortness of breath", "chronic fatigue", "chest pain", 
    "difficulty breathing", "back pain", "blurred vision", "tingling", "sweating", "frequent urination", 
    "burning sensations while urinating", "light sensitivity", "lightheadedness", "loss of appetite", "rash", 
    "itching", "heartburn", "coughing up blood", "wheezing", "numbness", "throat pain", "muscle stiffness", 
    "night sweats", "nausea", "vomiting", "abdominal pain", "frequent sneezing", "hearing loss", "constipation", 
    "urinary incontinence", "dry mouth", "difficulty swallowing", "coughing blood", "hoarseness", "confusion", 
    "drowsiness", "cold hands or feet", "dysphagia", "difficulty walking", "tremors", "chills", "bloody stool", 
    "leg cramps", "weight gain", "hair loss", "abnormal vaginal bleeding", "difficulty concentrating", 
    "sore throat", "wheezing", "fatigue", "muscle cramps", "cough with sputum", "coughing up phlegm", 
    "diarrhea", "vomiting", "hypertension", "dehydration", "swollen ankles", "blurry vision", "insomnia", 
    "leg swelling", "poor circulation", "tiredness", "leg swelling", "anxiety", "depression"}

    condition_keywords = {
        "chronic obstructive pulmonary disease", "heart attack", "irritable bowel syndrome", "rheumatoid arthritis", 
    "urinary tract infection", "chronic fatigue syndrome", "psoriasis", "asthma", "diabetes", "hypertension", 
    "cancer", "liver disease", "kidney failure", "stroke", "dementia", "arthritis", "pneumonia", "sepsis", 
    "epilepsy", "gastroesophageal reflux disease", "multiple sclerosis", "alzheimer's disease", "parkinson's disease", 
    "systemic lupus erythematosus", "diabetic neuropathy", "tuberculosis", "obesity", "cystic fibrosis", "hepatitis", 
    "meningitis", "sickle cell anemia", "hiv/aids", "celiac disease", "ulcerative colitis", "crohn's disease", 
    "chronic kidney disease", "fibromyalgia", "autoimmune disease", "anemia", "leukemia", "pneumothorax", 
    "lupus", "tetanus", "scleroderma", "rheumatic fever", "prostate cancer", "ovarian cancer", "breast cancer", 
    "gastric cancer", "non-hodgkin lymphoma", "hemophilia", "vitiligo", "severe malaria", "bronchitis", "gout", 
    "scabies", "hemorrhoids", "varicose veins", "hemophilia", "eczema", "chronic pain", "melanoma", "hearing loss", 
    "menstrual disorders", "anxiety", "depression", "bipolar disorder", "schizophrenia", "ptsd", "dyslexia", 
    "insomnia", "phobia", "hysteria", "attention deficit disorder", "migraines", "chronic back pain", "obstructive sleep apnea", 
    "epistaxis", "otitis media", "sinusitis", "bronchial asthma", "copd", "hypothyroidism", "hyperthyroidism", 
    "gout", "rickets", "hyperlipidemia", "cystitis", "spondylitis", "vascular dementia", "strokes", "fibroids"
    }

    medication_keywords = {
        "paracetamol", "ibuprofen", "aspirin", "metformin", "insulin", "atorvastatin", "omeprazole", "amoxicillin", 
    "losartan", "levothyroxine", "prednisone", "albuterol", "gabapentin", "sertraline", "amlodipine", "hydrochlorothiazide", 
    "clopidogrel", "lisinopril", "metoprolol", "simvastatin", "citalopram", "furosemide", "fluoxetine", "warfarin", 
    "trazodone", "cephalexin", "doxycycline", "rosuvastatin", "duloxetine", "pantoprazole", "hydrocodone", "tramadol", 
    "ciprofloxacin", "meloxicam", "escitalopram", "bupropion", "azithromycin", "ranitidine", "venlafaxine", "naproxen", 
    "ondansetron", "methotrexate", "mirtazapine", "spironolactone", "diazepam", "cyclobenzaprine", "diltiazem", 
    "metronidazole", "lorazepam", "morphine", "prednisolone", "famotidine", "baclofen", "clindamycin", "carvedilol", 
    "propranolol", "montelukast", "topiramate", "levofloxacin", "rivaroxaban", "apixaban", "cetirizine", 
    "diphenhydramine", "fentanyl", "hydroxyzine", "ivermectin", "ketorolac", "loratadine", "mefenamic acid", "methocarbamol", 
    "metformin xr", "metoclopramide", "nifedipine", "olmesartan", "phenytoin", "quetiapine", "risperidone", "sitagliptin", 
    "sulfasalazine", "tamsulosin", "terbinafine", "valacyclovir", "valsartan", "verapamil", "zolpidem", "tizanidine", 
    "clonazepam", "mometasone", "betamethasone", "fluticasone", "dexamethasone", "alprazolam", "acetaminophen", "esomeprazole", 
    "budesonide", "tiotropium", "cefuroxime", "erythromycin", "linezolid", "chlorpheniramine"
    } 

    # Generate n-grams (1-3 words)
    words = [token.text for token in doc]
    n_grams = []
    for n in range(1, 4):
        n_grams += [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

    symptoms = [term for term in n_grams if term in symptom_keywords]
    conditions = [term for term in n_grams if term in condition_keywords]
    medications = [term for term in n_grams if term in medication_keywords]

    return list(set(symptoms)), list(set(conditions)), list(set(medications))

file_path = r"C:/Users/MD.ZAID SHAIKH/Documents/transcription.txt"

# Read the text content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    text_content = file.read()

# Extract medical entities
output_data = extract_medical_entities(text_content)

# Convert the tuple to a dictionary with meaningful keys
data_dict = {
    "symptoms": output_data[0],
    "conditions": output_data[1],
    "medications": output_data[2]
}

json_file_path = "medical_entities.json"

# Save to JSON file with correct format
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(data_dict, json_file, indent=4, ensure_ascii=False)

print(f"JSON saved successfully at {json_file_path}")
