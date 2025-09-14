import json
from pathlib import Path

# مسیر فایل‌های ترجمه
LOCALE_DIR = Path(__file__).parent / "locales"

# بارگذاری فایل‌های ترجمه
translations = {}

for lang_file in LOCALE_DIR.glob("*.json"):
    lang_code = lang_file.stem  # مثال: en.json → "en"
    with open(lang_file, "r", encoding="utf-8") as f:
        translations[lang_code] = json.load(f)

def get_translation(lang: str, key: str) -> str:
    """پیام مناسب بر اساس زبان و کلید برمی‌گرداند."""
    if lang not in translations:
        lang = "en"  # fallback
    return translations[lang].get(key, key)
