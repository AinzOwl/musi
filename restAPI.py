from flask import Flask, request, jsonify
import io
import os
from pathlib import Path
import openai
import streamlit as st
from music_generator.config import AppConfig
from music_generator.generator import generate_note,export_abc_notations_to_file,convert_midi_to_music 

app = Flask(__name__)

@app.route('/generate_music', methods=['POST'])
def generate_music():
    openai_key = request.json['openai_key']
    music_topic = request.json['music_topic']
    text_engine = request.json.get('text_engine', 'gpt-3.5-turbo')
    max_attempts = request.json.get('max_attempts', 1)

    # Set the text engine
    AppConfig.set_text_engine(text_engine)

    path = "tmp"
    if not os.path.exists(path):
        os.mkdir(path)

    midi_data = None
    wav_data = None

    openai.api_key = openai_key
    with st.spinner(f"Generating music..."):

        architecture_components = None
        auto_components=True,
    
        user_input= f"You are a professional music composer. Please compose a music with this topic `{music_topic}`."
    
        music_generated = False
        successful_attempt_count = 0    
        failed_attempt_count = 0
        while successful_attempt_count < max_attempts:

            abc_notations = generate_note(user_input, architecture_components, auto_components=auto_components)

            if abc_notations is not None:

                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                midi_output_file = os.path.join(path, f"{timestamp}-success_music_attempt{successful_attempt_count}.mid")
                exported_midi_file = export_abc_notations_to_file(abc_notations, midi_output_file)

                if exported_midi_file is not None:

                    stem_name = Path(midi_output_file).stem
                    wav_output_file = os.path.join(path, f"{stem_name}.wav")
                    convert_midi_to_music(exported_midi_file, wav_output_file)
                    successful_attempt_count += 1
                else:
                    failed_attempt_count += 1
                    continue
            else:
                failed_attempt_count += 1
                continue
        if successful_attempt_count > 0:
            music_generated = True
            # Read the WAV file contents and store it in a BytesIO object
            with open(wav_output_file, "rb") as wav_file:
                wav_data = wav_file.read()

    if music_generated:
        response_data = {
            'success': True,
            'wav_data': wav_data
        }
    else:
        response_data = {
            'success': False
        }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
