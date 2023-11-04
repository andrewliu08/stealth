import os
from typing import List, Tuple

from app.constants.language import Language


def parse_language(lang: str) -> Language:
    lang = lang.lower()
    try:
        return Language(lang)
    except:
        raise ValueError("Unknown language: {}".format(lang))


def allowed_audio_file(filename):
    return (
        filename != ""
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ["m4a"]
    )


def save_resp_audio(file, filename: str) -> str:
    """
    Saves audio file in a designated folder and creates
    it if it doesn't exist.
    """
    RESP_AUDIO_DIR = "resp_audio"
    os.makedirs(RESP_AUDIO_DIR, exist_ok=True)

    file_path = os.path.join(RESP_AUDIO_DIR, filename)
    file.save(file_path)
    return file_path


def format_response_options(options: List[Tuple[str, str]]) -> dict:
    option_dicts = [
        {"resp_lang_content": option[0], "user_lang_content": option[1]}
        for option in options
    ]
    return {"options": option_dicts}
