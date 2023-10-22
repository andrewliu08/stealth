import requests
from typing import Dict

from app.language import Language

API_URL = "https://api-free.deepl.com/v2/translate"

DEEPL_LANG_TO_SOURCE_CODE: Dict[Language, str] = {
    Language.ENGLISH: "EN",
    Language.FRENCH: "FR",
    Language.MANDARIN: "ZH",
}

DEEPL_LANG_TO_TARGET_CODE: Dict[Language, str] = {
    Language.ENGLISH: "EN-US",
    Language.FRENCH: "FR",
    Language.MANDARIN: "ZH",
}


def deepl_translate(
    text: str, source_lang: Language, target_lang: Language, api_key: str
) -> requests.Response:
    """
    Example response JSON:
    {'translations': [{'detected_source_language': 'EN', 'text': 'Bonjour'}]}
    """
    source_code = DEEPL_LANG_TO_SOURCE_CODE[source_lang]
    target_code = DEEPL_LANG_TO_TARGET_CODE[target_lang]

    headers = {
        "Authorization": "DeepL-Auth-Key {}".format(api_key),
    }
    data = {
        "text": text,
        "source_lang": source_code,
        "target_lang": target_code,
    }

    response = requests.post(API_URL, headers=headers, data=data)
    return response