import os
import gradio as gr
from dotenv import load_dotenv

from tts.azure.config import LANGUAGES, load_language_labels, save_language_labels
from tts.azure.core import AzureTTS

# Load environment variables
load_dotenv()
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

# Prepare output directory
AUDIO_DIR = os.getenv("AUDIO_OUTPUT_DIR", "audio_outputs")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Azure TTS
azure_tts = AzureTTS(key=AZURE_KEY, region=AZURE_REGION)

# Load initial language labels
LANGUAGE_LABELS = load_language_labels()
DISPLAY_NAME_TO_CODE = {v: k for k, v in LANGUAGE_LABELS.items()}
USE_LANGUAGE_LABELS = bool(LANGUAGE_LABELS)

# === Helper Functions ===
def get_languages():
    return list(LANGUAGE_LABELS.values()) if USE_LANGUAGE_LABELS else list(LANGUAGES.keys())

def get_language_code(display_or_code):
    return DISPLAY_NAME_TO_CODE.get(display_or_code, display_or_code)

def get_voices(language_display):
    lang = get_language_code(language_display)
    return list(LANGUAGES[lang]["voices"].keys()) if lang in LANGUAGES else []

def get_styles(language_display, voice):
    lang = get_language_code(language_display)
    return LANGUAGES.get(lang, {}).get("voices", {}).get(voice, {}).get("styles", ["default"])

def update_voices(language_display):
    voices = get_voices(language_display)
    default_voice = voices[0] if voices else None
    updated_styles = update_styles(language_display, default_voice)["choices"] if default_voice else []
    default_style = updated_styles[0] if updated_styles else None
    return gr.update(choices=voices, value=default_voice), gr.update(choices=updated_styles, value=default_style)

def update_styles(language_display, voice):
    styles = get_styles(language_display, voice)
    return gr.update(choices=styles, value=styles[0] if styles else "default")

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

def refresh_language_labels():
    global LANGUAGE_LABELS, DISPLAY_NAME_TO_CODE
    LANGUAGE_LABELS = load_language_labels()
    DISPLAY_NAME_TO_CODE = {v: k for k, v in LANGUAGE_LABELS.items()}

def refresh_languages_dropdown():
    refresh_language_labels()
    return gr.update(choices=get_languages())

def save_and_refresh_language(code, label):
    LANGUAGE_LABELS[code] = label
    save_language_labels(LANGUAGE_LABELS)
    refresh_language_labels()
    return [[k, v] for k, v in LANGUAGE_LABELS.items()], gr.update(choices=get_languages()), gr.update(choices=get_languages())

def reload_label_table():
    refresh_language_labels()
    return [[k, v] for k, v in LANGUAGE_LABELS.items()], gr.update(choices=get_languages()), gr.update(choices=get_languages())

# def delete_language(label_to_delete):
#     lang_code = DISPLAY_NAME_TO_CODE.get(label_to_delete)
#     if lang_code and lang_code in LANGUAGE_LABELS:
#         del LANGUAGE_LABELS[lang_code]
#         save_language_labels(LANGUAGE_LABELS)
#         refresh_language_labels()
#     return [[k, v] for k, v in LANGUAGE_LABELS.items()], gr.update(choices=get_languages()), gr.update(choices=get_languages())

def delete_language(label_to_delete):
    if not label_to_delete.strip():
        return [[k, v] for k, v in LANGUAGE_LABELS.items()], gr.update(), gr.update()

    lang_code = DISPLAY_NAME_TO_CODE.get(label_to_delete)
    if lang_code and lang_code in LANGUAGE_LABELS:
        del LANGUAGE_LABELS[lang_code]
        save_language_labels(LANGUAGE_LABELS)
        refresh_language_labels()
    return [[k, v] for k, v in LANGUAGE_LABELS.items()], gr.update(choices=get_languages()), gr.update(
        choices=get_languages())

# === Audio Library ===
def list_audio_files():
    """
    Returns a sorted list of audio file paths from the AUDIO_DIR directory.
    """
    files = []
    for fname in sorted(os.listdir(AUDIO_DIR), reverse=True):
        if fname.endswith((".mp3", ".wav", ".ogg")):
            files.append(os.path.join(AUDIO_DIR, fname))
    return files

def delete_audio_file(filepath):
    """
    Deletes the specified audio file.
    """
    try:
        os.remove(filepath)
        return f"Deleted: {os.path.basename(filepath)}"
    except Exception as e:
        return f"Error: {str(e)}"

def update_audio_list():
    """
    Returns an updated list of audio files for the dropdown.
    """
    files = list_audio_files()
    return gr.update(choices=files, value=files[0] if files else None)

# === Default UI values ===
default_lang_display = get_languages()[0]
default_voices = get_voices(default_lang_display)
default_voice = default_voices[0] if default_voices else None
default_styles = get_styles(default_lang_display, default_voice) if default_voice else ["default"]
default_style = default_styles[0] if default_styles else "default"

# === Gradio Interface ===
with gr.Blocks() as demo:
    with gr.Tab("TTS"):
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

    with gr.Tab("Edit Languages"):
        with gr.Row():
            # lang_code_input = gr.Textbox(label="Language Code", placeholder="e.g. ar-KW")
            # lang_label_input = gr.Textbox(label="Display Name", placeholder="e.g. Arabic (Kuwait)")
            # save_button = gr.Button("Save / Update")
            with gr.Column(scale=1):
                lang_code_input = gr.Textbox(label="Language Code", placeholder="e.g. ar-KW")
                lang_label_input = gr.Textbox(label="Display Name", placeholder="e.g. Arabic (Kuwait)")
                save_button = gr.Button("Save / Update", scale=1)
                delete_lang_dropdown = gr.Dropdown(label="Delete Language", choices=get_languages())
                delete_button = gr.Button("Delete Selected Language")
            with gr.Column(scale=1):
                label_table = gr.Dataframe(headers=["Code", "Label"], datatype=["str", "str"],
                                           value=[[k, v] for k, v in LANGUAGE_LABELS.items()])

        # with gr.Row():
        #     delete_lang_dropdown = gr.Dropdown(label="Delete Language", choices=get_languages())
        #     delete_button = gr.Button("Delete Selected Language")

        with gr.Row():
            reload_button = gr.Button("Reload")

        save_button.click(fn=save_and_refresh_language, inputs=[lang_code_input, lang_label_input],
                          outputs=[label_table, language_dropdown, delete_lang_dropdown])

        reload_button.click(fn=reload_label_table,
                            outputs=[label_table, language_dropdown, delete_lang_dropdown])

        delete_button.click(fn=delete_language, inputs=[delete_lang_dropdown],
                            outputs=[label_table, language_dropdown, delete_lang_dropdown])

    with gr.Tab("Audio Library"):
        file_list = gr.Dropdown(choices=list_audio_files(), label="Select audio file")
        audio_player = gr.Audio()
        delete_btn = gr.Button("Delete selected file")
        refresh_btn = gr.Button("Refresh list")
        status_text = gr.Markdown("")

        file_list.change(lambda f: f, file_list, audio_player)
        delete_btn.click(delete_audio_file, file_list, status_text).then(
            update_audio_list, None, file_list
        )
        refresh_btn.click(update_audio_list, None, file_list)


if __name__ == "__main__":
    demo.launch()
