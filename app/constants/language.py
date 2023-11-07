from enum import Enum


class Language(Enum):
    ARABIC = "arabic"
    BASHKIR = "bashkir"
    BASQUE = "basque"
    BELARUSIAN = "belarusian"
    BULGARIAN = "bulgarian"
    CANTONESE = "cantonese"
    CATALAN = "catalan"
    CROATIAN = "croation"
    CZECH = "czech"
    DANISH = "danish"
    DUTCH = "dutch"
    ENGLISH = "english"
    ESPERANTO = "esperanto"
    ESTONIAN = "estonian"
    FINNISH = "finnish"
    FRENCH = "french"
    GALICIAN = "galician"
    GERMAN = "german"
    GREEK = "greek"
    HINDI = "hindi"
    HUNGARIAN = "hungarian"
    ICELANDIC = "icelandic"
    INDONESIAN = "indonesian"
    INTERLINGUA = "interlingua"
    ITALIAN = "italian"
    JAPANESE = "japanese"
    KOREAN = "korean"
    LATVIAN = "latvian"
    LITHUANIAN = "lithuanian"
    MALAY = "malay"
    MANDARIN = "mandarin"
    MARATHI = "marathi"
    MONGOLIAN = "mongolian"
    NORWEGIAN = "norwegian"
    PERSIAN = "persian"
    POLISH = "polish"
    PORTUGUESE = "portuguese"
    ROMANIAN = "romanian"
    RUSSIAN = "russian"
    SLOVAK = "slovak"
    SLOVENIAN = "slovenian"
    SPANISH = "spanish"
    SWEDISH = "swedish"
    TAMIL = "TAMIL"
    THAI = "thai"
    TURKISH = "turkish"
    UYGHUR = "uyghur"
    UKRAINIAN = "ukrainian"
    VIETNAMESE = "vietnamese"
    WELSH = "welsh"


# from app.avr.speechmatics import SPEECHMATICS_LANG_TO_CODE
# from app.translation.deepl import DEEPL_LANG_TO_SOURCE_CODE, DEEPL_LANG_TO_TARGET_CODE
# from app.tts.aws_polly import AWS_POLLY_LANG_TO_VOICE


# def get_language_intersection():
#     """Get the intersection of languages supported by all APIs."""
#     speechmatics_langs = set(SPEECHMATICS_LANG_TO_CODE.keys())
#     deepl_langs = set(DEEPL_LANG_TO_SOURCE_CODE.keys())
#     polly_langs = set(AWS_POLLY_LANG_TO_VOICE.keys())
#     return speechmatics_langs.intersection(deepl_langs, polly_langs)
