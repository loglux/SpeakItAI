import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "language_labels.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    LANGUAGES = json.load(f)

# Loading language labels
def load_language_labels():
    try:
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

LANGUAGE_LABELS = load_language_labels()

def save_language_labels(new_labels: dict):
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(new_labels, f, ensure_ascii=False, indent=4)
