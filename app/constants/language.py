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

    @property
    def iso_639_1(self) -> str:
        return ISO_639_1[self]


ISO_639_1 = {
    Language.ARABIC: "ar",
    Language.BASHKIR: "ba",
    Language.BASQUE: "eu",
    Language.BELARUSIAN: "be",
    Language.BULGARIAN: "bg",
    Language.CANTONESE: "zh",
    Language.CATALAN: "ca",
    Language.CROATIAN: "hr",
    Language.CZECH: "cs",
    Language.DANISH: "da",
    Language.DUTCH: "nl",
    Language.ENGLISH: "en",
    Language.ESPERANTO: "eo",
    Language.ESTONIAN: "et",
    Language.FINNISH: "fi",
    Language.FRENCH: "fr",
    Language.GALICIAN: "gl",
    Language.GERMAN: "de",
    Language.GREEK: "el",
    Language.HINDI: "hi",
    Language.HUNGARIAN: "hu",
    Language.ICELANDIC: "is",
    Language.INDONESIAN: "id",
    Language.INTERLINGUA: "ia",
    Language.ITALIAN: "it",
    Language.JAPANESE: "ja",
    Language.KOREAN: "ko",
    Language.LATVIAN: "lv",
    Language.LITHUANIAN: "lt",
    Language.MALAY: "ms",
    Language.MANDARIN: "zh",
    Language.MARATHI: "mr",
    Language.MONGOLIAN: "mn",
    Language.NORWEGIAN: "no",
    Language.PERSIAN: "fa",
    Language.POLISH: "pl",
    Language.PORTUGUESE: "pt",
    Language.ROMANIAN: "ro",
    Language.RUSSIAN: "ru",
    Language.SLOVAK: "sk",
    Language.SLOVENIAN: "sl",
    Language.SPANISH: "es",
    Language.SWEDISH: "sv",
    Language.TAMIL: "ta",
    Language.THAI: "th",
    Language.TURKISH: "tr",
    Language.UYGHUR: "ug",
    Language.UKRAINIAN: "uk",
    Language.VIETNAMESE: "vi",
    Language.WELSH: "cy",
}


# from app.avr.speechmatics import SPEECHMATICS_LANG_TO_CODE
# from app.translation.deepl import DEEPL_LANG_TO_SOURCE_CODE, DEEPL_LANG_TO_TARGET_CODE
# from app.tts.aws_polly import AWS_POLLY_LANG_TO_VOICE


# def get_language_intersection():
#     """Get the intersection of languages supported by all APIs."""
#     speechmatics_langs = set(SPEECHMATICS_LANG_TO_CODE.keys())
#     deepl_langs = set(DEEPL_LANG_TO_SOURCE_CODE.keys())
#     polly_langs = set(AWS_POLLY_LANG_TO_VOICE.keys())
#     return speechmatics_langs.intersection(deepl_langs, polly_langs)
