from flask import Flask, render_template, request, send_file
from piper import PiperVoice

import wave
import io
import os
from datetime import datetime

app = Flask(__name__)

# Initialize Piper TTS engine
VOICE_MODEL_PATH = "voices/en_GB-alan-medium.onnx"
VOICE_CONFIG_PATH = "voices/en_GB-alan-medium.onnx.json"

# Create a directory for audio files if it doesn't exist
AUDIO_DIR = "./output/audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    tts = PiperVoice.load(VOICE_MODEL_PATH, config_path=VOICE_CONFIG_PATH)
except Exception as e:
    print(f"Error loading voice model: {e}")
    print("Please ensure you have downloaded the voice model files from Hugging Face")
    exit(1)

@app.route('/', methods=['GET', 'POST'])
def home():
    audio_path = None
    text = ""
    error = None
    
    if request.method == 'POST':
        text = request.form['text']
        if text:
            try:
                # Generate unique filename based on timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"
                file_path = os.path.join(AUDIO_DIR, filename)
                
                # Generate speech directly to WAV file
                with open(file_path, 'wb') as wav_file:
                    with wave.Wave_write(wav_file) as wav:
                        tts.synthesize(text, wav)
                
                # Pass the filename to the template
                audio_path = filename
                
            except Exception as e:
                error = f"Error generating speech: {str(e)}"
            
    return render_template('index.html', audio_path=audio_path, text=text, error=error)

@app.route('/library')
def audio_library():
    """Display all saved audio files"""
    audio_files = []
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.wav'):
            file_path = os.path.join(AUDIO_DIR, filename)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            audio_files.append({
                'filename': filename,
                'created_at': creation_time.strftime("%Y-%m-%d %H:%M:%S"),
                'size': f"{os.path.getsize(file_path) / 1024:.1f} KB"
            })
    
    # Sort files by creation time (newest first)
    audio_files.sort(key=lambda x: x['created_at'], reverse=True)
    return render_template('library.html', audio_files=audio_files)

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files from the audio directory"""
    try:
        return send_file(
            os.path.join(AUDIO_DIR, filename),
            mimetype='audio/wav',
            as_attachment=False  # Stream in browser instead of downloading
        )
    except Exception as e:
        return f"Error serving audio file: {str(e)}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501, debug=True)