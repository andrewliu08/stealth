from app.constants.language import Language


def parse_language(lang: str) -> Language:
    lang = lang.lower()
    if lang == "english":
        return Language.ENGLISH
    elif lang == "mandarin":
        return Language.MANDARIN
    elif lang == "french":
        return Language.FRENCH
    else:
        raise ValueError("Unknown language: {}".format(lang))
