"""
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json
pip install google-cloud-texttospeech
"""

from google.cloud import texttospeech
import tempfile

class GoogleTTS:
    def __init__(self, credentials_path: str):
        self.client = texttospeech.TextToSpeechClient.from_service_account_file(credentials_path)

    def synthesize(self, text: str, voice_code="ru-RU-Wavenet-C", speaking_rate=1.0, pitch=0.0) -> str:
        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_code,
            name=voice_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speaking_rate,
            pitch=pitch
        )

        response = self.client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )

        file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="audio_outputs")
        with open(file.name, "wb") as out:
            out.write(response.audio_content)

        return file.name
