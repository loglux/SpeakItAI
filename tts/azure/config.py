import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Load voice configuration
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    LANGUAGES = json.load(f)

# Human-readable labels for language codes
LANGUAGE_LABELS = {
    "en-GB": "English (UK)",
    "en-US": "English (US)",
    "en-IE": "English (IE)",
    "ru-RU": "Russian",
    "fr-FR": "French",
    "de-DE": "German",
    "es-ES": "Spanish",
    "it-IT": "Italian",
    "ja-JP": "Japanese",
    "zh-CN": "Chinese (Simplified)",
    # Add more as needed
}
