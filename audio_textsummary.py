import os
import base64
import json
import requests
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# This line loads the GEMINI_API_KEY from your .env file
load_dotenv()

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'a_random_secret_key_for_flask' # Needed for flashing messages

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_audio(file_path: str, api_key: str) -> str:
    """Sends audio data to the Gemini API for transcription."""
    print(f"Transcribing audio from: {file_path}")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    with open(file_path, "rb") as audio_file:
        encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

    payload = {
        "contents": [{
            "parts": [
                {"text": "Transcribe this conversation. Provide only the raw text of the conversation."},
                {"inline_data": {"mime_type": "audio/wav", "data": encoded_audio}}
            ]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        transcript = result['candidates'][0]['content']['parts'][0]['text']
        print("Transcription successful.")
        return transcript.strip()
    except Exception as e:
        print(f"API request error during transcription: {e}")
        return None

def summarize_transcript(transcript: str, api_key: str) -> dict:
    """Analyzes a call transcript using the Gemini API."""
    print("Summarizing transcript...")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

    prompt = """
    You are an expert AI assistant for an insurance agent. Your task is to analyze the following call transcript and extract key information in a structured JSON format.
    Transcript:
    ---
    {transcript}
    ---
    Based on the transcript, provide a JSON object with keys like "summary", "clientName", "task", "carDetails", "actionItems", etc.
    """.format(transcript=transcript)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result_json_string = response.json()['candidates'][0]['content']['parts'][0]['text']
        print("Summarization successful.")
        return json.loads(result_json_string)
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

# THIS IS THE CRITICAL LINE THAT FIXES THE ERROR
@app.route('/', methods=['GET', 'POST'])
def upload_and_process():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                flash('GEMINI_API_KEY is not set in the environment. Make sure you have a .env file.', 'error')
                return redirect(request.url)

            transcript = transcribe_audio(filepath, api_key)
            if not transcript:
                flash('Failed to transcribe the audio. Check the console for errors.', 'error')
                return redirect(request.url)

            summary = summarize_transcript(transcript, api_key)
            if not summary:
                flash('Failed to summarize the transcript. Check the console for errors.', 'error')
                return redirect(request.url)

            summary_str = json.dumps(summary, indent=2)
            
            return render_template('index.html', transcript=transcript, summary=summary_str)
        else:
            flash('Invalid file type. Please upload a .wav file.', 'error')
            return redirect(request.url)
            
    # This is what happens on a GET request (when the page first loads)
    return render_template('index.html', transcript=None, summary=None)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5001, debug=True)
