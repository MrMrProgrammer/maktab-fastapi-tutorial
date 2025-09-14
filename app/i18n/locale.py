from fastapi import Request, Depends
from app.i18n import get_translation

def get_locale(request: Request):
    lang = request.headers.get("Accept-Language")
    if lang and lang in ["en", "fa"]:
        return lang
    lang = request.query_params.get("lang")
    if lang and lang in ["en", "fa"]:
        return lang
    return "en"

def translate(key: str, lang: str = Depends(get_locale)):
    return get_translation(lang, key)
