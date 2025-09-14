import json
from pathlib import Path

LOCALES = {}

def load_translations():
    path = Path(__file__)
    for file in path.glob("*.json"):
        lang = file.stem
        with open(file, "r", encoding="utf-8") as f:
            LOCALES[lang] = json.load(f)

def get_translation(lang: str, key: str) -> str:
    return LOCALES.get(lang, LOCALES.get("en", {})).get(key, key)

load_translations()
