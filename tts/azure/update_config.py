import os
import json
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

class AzureVoiceConfigUpdater:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv("AZURE_KEY")
        self.region = os.getenv("AZURE_REGION")
        if not self.key or not self.region:
            raise ValueError("Azure credentials are missing in the .env file")
        self.speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)

    def fetch_voices(self):
        print("Fetching voices from Azure...")
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        voice_list = synthesizer.get_voices_async().get().voices
        return voice_list

    def build_config(self, voices):
        languages = {}
        for voice in voices:
            lang = voice.locale
            voice_label = voice.local_name  # Corrected attribute
            voice_entry = {
                "id": voice.name,
                "gender": voice.gender.name,
                "style_list": voice.style_list if voice.style_list else ["default"]
            }

            if lang not in languages:
                languages[lang] = {"voices": {}}

            languages[lang]["voices"][voice_label] = {
                "id": voice_entry["id"],
                "gender": voice_entry["gender"],
                "styles": voice_entry["style_list"]
            }

        return languages

    def save_config(self, data, output_path="config.json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Configuration saved to {output_path}")

if __name__ == "__main__":
    updater = AzureVoiceConfigUpdater()
    voice_data = updater.fetch_voices()
    config = updater.build_config(voice_data)
    updater.save_config(config)
