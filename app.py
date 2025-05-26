import os
import gradio as gr
from dotenv import load_dotenv
from tts.core import AzureTTS
from tts.config import VOICES, STYLES, RATES, PITCHES

load_dotenv()
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

os.makedirs("audio_outputs", exist_ok=True)
azure_tts = AzureTTS(key=AZURE_KEY, region=AZURE_REGION)

def generate_audio(text_input, file, voice_label, style, rate, pitch):
    try:
        if file:
            with open(file.name, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = text_input

        if not text.strip():
            return "Error: Please provide text or upload a file."

        voice = VOICES[voice_label]
        return azure_tts.synthesize(text, voice, style, rate, pitch)

    except Exception as e:
        return f"Error: {str(e)}"

gr.Interface(
    fn=generate_audio,
    inputs=[
        gr.Textbox(label="Enter your text", lines=8),
        gr.File(label="Or upload a .txt file", type="filepath", file_types=[".txt"]),
        gr.Dropdown(label="Select Voice", choices=list(VOICES.keys()), value="Ryan (Male)"),
        gr.Dropdown(label="Select Speaking Style", choices=STYLES, value="default"),
        gr.Dropdown(label="Speech Rate", choices=RATES, value="0%"),
        gr.Dropdown(label="Pitch", choices=PITCHES, value="0%")
    ],
    outputs=gr.Audio(type="filepath"),
    title="SpeakItAI – Neural TTS",
    description="Convert text to realistic speech using Microsoft Azure.",
    allow_flagging="never"
).launch()
