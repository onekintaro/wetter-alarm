import json
import aiofiles
import os

async def load_translations(lang):
    translations_path = f'custom_components/wetter_alarm/translations/{lang}.json'
    if os.path.exists(translations_path):
        async with aiofiles.open(translations_path, 'r') as file:
            content = await file.read()
            return json.loads(content)
    return {}