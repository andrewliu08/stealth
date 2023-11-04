import requests
from typing import Dict

from app.constants.language import Language

API_URL = "https://api-free.deepl.com/v2/translate"

# https://www.deepl.com/docs-api/translate-text
DEEPL_LANG_TO_SOURCE_CODE: Dict[Language, str] = {
    Language.BULGARIAN: "BG",
    Language.CANTONESE: "ZH",
    Language.CZECH: "CS",
    Language.DANISH: "DA",
    Language.DUTCH: "NL",
    Language.ENGLISH: "EN",
    Language.ESTONIAN: "ET",
    Language.FINNISH: "FI",
    Language.FRENCH: "FR",
    Language.GERMAN: "DE",
    Language.GREEK: "EL",
    Language.HUNGARIAN: "HU",
    Language.INDONESIAN: "ID",
    Language.ITALIAN: "IT",
    Language.JAPANESE: "JA",
    Language.KOREAN: "KO",
    Language.LATVIAN: "LV",
    Language.LITHUANIAN: "LT",
    Language.MANDARIN: "ZH",
    Language.NORWEGIAN: "NB",
    Language.POLISH: "PL",
    Language.PORTUGUESE: "PT",
    Language.ROMANIAN: "RO",
    Language.RUSSIAN: "RU",
    Language.SLOVAK: "SK",
    Language.SLOVENIAN: "SL",
    Language.SPANISH: "ES",
    Language.SWEDISH: "SV",
    Language.TURKISH: "TR",
    Language.UKRAINIAN: "UK",
}

DEEPL_LANG_TO_TARGET_CODE: Dict[Language, str] = {
    Language.BULGARIAN: "BG",
    Language.CANTONESE: "ZH",
    Language.CZECH: "CS",
    Language.DANISH: "DA",
    Language.DUTCH: "NL",
    Language.ENGLISH: "EN-US",
    Language.ESTONIAN: "ET",
    Language.FINNISH: "FI",
    Language.FRENCH: "FR",
    Language.GERMAN: "DE",
    Language.GREEK: "EL",
    Language.HUNGARIAN: "HU",
    Language.INDONESIAN: "ID",
    Language.ITALIAN: "IT",
    Language.JAPANESE: "JA",
    Language.KOREAN: "KO",
    Language.LATVIAN: "LV",
    Language.LITHUANIAN: "LT",
    Language.MANDARIN: "ZH",
    Language.NORWEGIAN: "NB",
    Language.POLISH: "PL",
    Language.PORTUGUESE: "PT-PT",
    Language.ROMANIAN: "RO",
    Language.RUSSIAN: "RU",
    Language.SLOVAK: "SK",
    Language.SLOVENIAN: "SL",
    Language.SPANISH: "ES",
    Language.SWEDISH: "SV",
    Language.TURKISH: "TR",
    Language.UKRAINIAN: "UK",
}


def extract_translation_from_deepl_response(response: requests.Response) -> str:
    """
    Example response JSON:
    {'translations': [{'detected_source_language': 'EN', 'text': 'Bonjour'}]}
    """
    translation = response.json()["translations"][0]["text"]
    return translation


def deepl_translate(
    text: str, source_lang: Language, target_lang: Language, api_key: str
) -> requests.Response:
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
    return extract_translation_from_deepl_response(response)
