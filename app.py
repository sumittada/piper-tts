from flask import Flask, render_template, request, send_file
from piper import PiperVoice

import wave
import io
import os
from datetime import datetime

app = Flask(__name__)

# Initialize Piper TTS engine
# Paths are now relative to the voices directory
VOICE_MODEL_PATH = "voices/en_GB-alba-medium.onnx"
VOICE_CONFIG_PATH = "voices/en_GB-alba-medium.onnx.json"

try:
    tts = PiperVoice.load(VOICE_MODEL_PATH, config_path=VOICE_CONFIG_PATH)
except Exception as e:
    print(f"Error loading voice model: {e}")
    print("Please ensure you have downloaded the voice model files from Hugging Face")
    exit(1)

@app.route('/', methods=['GET', 'POST'])
def home():
    audio_file = None
    text = ""
    error = None
    
    if request.method == 'POST':
        text = request.form['text']
        if text:
            try:
                # Generate unique filename based on timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_path = f"output/temp_audio_{timestamp}.wav"
                
                # Generate speech directly to WAV file
                with open(temp_path, 'wb') as wav_file:
                    with wave.Wave_write(wav_file) as wav:
                        tts.synthesize(text, wav)
                
                # Read the file and delete it
                with open(temp_path, 'rb') as audio:
                    audio_file = audio.read()
                #os.remove(temp_path)
                
            except Exception as e:
                error = f"Error generating speech: {str(e)}"
            
    return render_template('index.html', audio_file=temp_path, text=text, error=error)

# Route to serve the audio file
@app.route('/audio')
def serve_audio():
    audio_data = request.args.get('data', '').encode()
    return send_file(
        io.BytesIO(audio_data),
        mimetype='audio/wav',
        as_attachment=True,
        download_name='tts_output.wav'
    )

if __name__ == '__main__':
    # Modified to run on all interfaces in Docker
    app.run(host='0.0.0.0', port=5501, debug=True)