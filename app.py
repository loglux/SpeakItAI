import os
from dotenv import load_dotenv
import gradio as gr
from tts.azure.config import LANGUAGES

# Optional: import custom language labels if defined
try:
    from tts.azure.config import LANGUAGE_LABELS
except ImportError:
    LANGUAGE_LABELS = {}

from tts.azure.core import AzureTTS

# Load environment variables
load_dotenv()
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

# Prepare output directory
os.makedirs("audio_outputs", exist_ok=True)

# Initialize Azure TTS
azure_tts = AzureTTS(key=AZURE_KEY, region=AZURE_REGION)

# Reverse mapping for label-to-code lookup
DISPLAY_NAME_TO_CODE = {v: k for k, v in LANGUAGE_LABELS.items()}
USE_LANGUAGE_LABELS = bool(LANGUAGE_LABELS)

# Helper functions
def get_languages():
    return list(LANGUAGE_LABELS.values()) if USE_LANGUAGE_LABELS else list(LANGUAGES.keys())

def get_language_code(display_or_code):
    return DISPLAY_NAME_TO_CODE.get(display_or_code, display_or_code)

def get_voices(language_display):
    lang = get_language_code(language_display)
    return list(LANGUAGES[lang]["voices"].keys())

def get_styles(language_display, voice):
    lang = get_language_code(language_display)
    return LANGUAGES[lang]["voices"][voice].get("styles", ["default"])

def update_voices(language_display):
    voices = get_voices(language_display)
    default_voice = voices[0] if voices else None
    updated_styles = update_styles(language_display, default_voice)["choices"] if default_voice else []
    default_style = updated_styles[0] if updated_styles else None
    return gr.update(choices=voices, value=default_voice), gr.update(choices=updated_styles, value=default_style)

def update_styles(language_display, voice):
    styles = get_styles(language_display, voice)
    return gr.update(choices=styles, value=styles[0])

def generate_audio(text_input, file, language_display, voice_label, style, rate, pitch):
    try:
        if file is not None:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = text_input

        if not text.strip():
            return "Error: Please provide text input or upload a file."

        lang = get_language_code(language_display)
        voice_id = LANGUAGES[lang]["voices"][voice_label]["id"]
        return azure_tts.synthesize(text, voice_id, style, rate, pitch)

    except Exception as e:
        return f"Error: {str(e)}"

# Default dropdown values
default_lang_display = get_languages()[0]
default_voices = get_voices(default_lang_display)
default_voice = default_voices[0] if default_voices else None
default_styles = get_styles(default_lang_display, default_voice) if default_voice else ["default"]
default_style = default_styles[0] if default_styles else "default"

# Build interface
with gr.Blocks() as demo:
    with gr.Row():
        language_dropdown = gr.Dropdown(label="Select Language", choices=get_languages(), value=default_lang_display)
        voice_dropdown = gr.Dropdown(label="Select Voice", choices=default_voices, value=default_voice)
        style_dropdown = gr.Dropdown(label="Speaking Style", choices=default_styles, value=default_style)

    with gr.Row():
        rate_dropdown = gr.Dropdown(label="Speech Rate", choices=["-20%", "-10%", "0%", "+10%", "+20%"], value="0%")
        pitch_dropdown = gr.Dropdown(label="Pitch", choices=["-20%", "-10%", "0%", "+10%", "+20%"], value="0%")

    with gr.Row():
        text_input = gr.Textbox(label="Enter your text", lines=8, placeholder="You can type here...")
        file_input = gr.File(label="Or upload a .txt file", type="filepath", file_types=[".txt"])

    output_audio = gr.Audio(type="filepath")

    submit_button = gr.Button("Generate Audio")
    submit_button.click(
        fn=generate_audio,
        inputs=[text_input, file_input, language_dropdown, voice_dropdown, style_dropdown, rate_dropdown, pitch_dropdown],
        outputs=[output_audio]
    )

    language_dropdown.change(fn=update_voices, inputs=[language_dropdown], outputs=[voice_dropdown, style_dropdown])
    voice_dropdown.change(fn=update_styles, inputs=[language_dropdown, voice_dropdown], outputs=[style_dropdown])

if __name__ == "__main__":
    demo.launch()
