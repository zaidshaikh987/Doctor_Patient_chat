from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from audio_integrate import record_audio, transcribe_audio
from medical_entity import extract_medical_entities
from soap_generator import generate_soap_with_gemini
from evidence_synthesis import generate_evidence_report
import uuid

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/record', methods=['POST'])
def handle_record():
    """Endpoint to record and save audio"""
    try:
        # Generate unique filename
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Record audio (duration from request or default)
        duration = request.json.get('duration', 15)
        record_audio(filepath, duration)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'message': 'Audio recorded successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Recording failed: {str(e)}'
        }), 500

@app.route('/api/transcribe', methods=['POST'])
def handle_transcribe():
    """Endpoint to transcribe audio"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
            
        audio_file = request.files['file']
        
        if not allowed_file(audio_file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Invalid file type'
            }), 400
            
        # Save the file temporarily
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Transcribe the audio
        transcription = transcribe_audio(filepath)
        
        # Save transcription to file
        transcript_filename = f"transcript_{filename.split('.')[0]}.txt"
        transcript_path = os.path.join(app.config['UPLOAD_FOLDER'], transcript_filename)
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        
        return jsonify({
            'status': 'success',
            'transcription': transcription,
            'transcript_file': transcript_filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Transcription failed: {str(e)}'
        }), 500

@app.route('/api/analyze', methods=['POST'])
def handle_analyze():
    """Endpoint to analyze text and generate medical entities"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'No text provided for analysis'
            }), 400
            
        # Extract medical entities
        symptoms, conditions, medications = extract_medical_entities(text)
        
        # Generate JSON output
        entities_data = {
            'symptoms': symptoms,
            'conditions': conditions,
            'medications': medications
        }
        
        # Save to JSON file
        json_filename = f"entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, indent=4)
        
        return jsonify({
            'status': 'success',
            'entities': entities_data,
            'json_file': json_filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/generate-soap', methods=['POST'])
def handle_generate_soap():
    """Endpoint to generate SOAP note"""
    try:
        data = request.json
        text = data.get('text', '')
        entities = data.get('entities', {})
        
        if not text or not entities:
            return jsonify({
                'status': 'error',
                'message': 'Missing required data'
            }), 400
            
        # Generate SOAP note
        soap_note = generate_soap_with_gemini(text, entities)
        
        return jsonify({
            'status': 'success',
            'soap_note': soap_note
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'SOAP generation failed: {str(e)}'
        }), 500

@app.route('/api/generate-evidence', methods=['POST'])
def handle_generate_evidence():
    """Endpoint to generate evidence-based recommendations"""
    try:
        data = request.json
        entities = data.get('entities', {})
        
        if not entities:
            return jsonify({
                'status': 'error',
                'message': 'No entities provided'
            }), 400
            
        # Generate evidence report
        evidence_report = generate_evidence_report(entities)
        
        return jsonify({
            'status': 'success',
            'evidence_report': evidence_report
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Evidence generation failed: {str(e)}'
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def handle_generate_report():
    """Endpoint to generate complete patient report"""
    try:
        data = request.json
        text = data.get('text', '')
        entities = data.get('entities', {})
        soap_note = data.get('soap_note', '')
        evidence = data.get('evidence', '')
        
        if not all([text, entities, soap_note, evidence]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required data'
            }), 400
            
        # Generate comprehensive report
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_report = f"""PATIENT MEDICAL REPORT
Generated on: {report_date}
==========================================

PATIENT SUMMARY:
{text}

IDENTIFIED MEDICAL ENTITIES:
• Symptoms: {', '.join(entities.get('symptoms', [])) or 'None identified'}
• Conditions: {', '.join(entities.get('conditions', [])) or 'None identified'}
• Medications: {', '.join(entities.get('medications', [])) or 'None identified'}

CLINICAL ASSESSMENT (SOAP FORMAT):
{soap_note}

EVIDENCE-BASED RECOMMENDATIONS:
{evidence}

PATIENT-FRIENDLY SUMMARY:
• Follow your prescribed medications
• Monitor your symptoms and report any changes
• Schedule follow-up appointments as recommended
• Contact your healthcare provider with any concerns"""
        
        # Save report to file
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        return jsonify({
            'status': 'success',
            'report': full_report,
            'report_file': report_filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Report generation failed: {str(e)}'
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint to download generated files"""
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'File download failed: {str(e)}'
        }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)