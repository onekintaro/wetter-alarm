import json
import os

def load_translations(lang):
    translations_path = f'custom_components/wetter_alarm/translations/{lang}.json'
    if os.path.exists(translations_path):
        with open(translations_path, 'r') as file:
            return json.load(file)
    return {}
