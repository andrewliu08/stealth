from openai import OpenAI

from app.constants.language import Language


def openai_avr(openai_client: OpenAI, audio_file: str, language: Language) -> str:
    audio_file = open(audio_file, "rb")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1",
        language=language.iso_639_1,
        file=audio_file,
        response_format="text",
    )
    return transcript
