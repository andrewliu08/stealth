from typing import Dict

import speechmatics

from app.constants.language import Language

# https://docs.speechmatics.com/introduction/supported-languages
SPEECHMATICS_LANG_TO_CODE: Dict[Language, str] = {
    Language.ARABIC: "ar",
    Language.BASHKIR: "ba",
    Language.BASQUE: "eu",
    Language.BELARUSIAN: "be",
    Language.BULGARIAN: "bg",
    Language.CANTONESE: "yue",
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
    Language.INDONESIAN: "id",
    Language.INTERLINGUA: "ia",
    Language.ITALIAN: "it",
    Language.JAPANESE: "ja",
    Language.KOREAN: "ko",
    Language.LATVIAN: "lv",
    Language.LITHUANIAN: "lt",
    Language.MALAY: "ms",
    Language.MANDARIN: "cmn",
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
REST_API_URL = "https://asr.api.speechmatics.com/v2"
WS_API_URL = "wss://eu2.rt.speechmatics.com/v2"


def create_connection_settings(
    api_url: str, api_key: str
) -> speechmatics.models.ConnectionSettings:
    return speechmatics.models.ConnectionSettings(
        url=api_url,
        auth_token=api_key,
    )


def speechmatics_file_avr(
    settings: speechmatics.models.ConnectionSettings,
    audio_file: str,
    language: Language,
) -> str:
    # Define transcription parameters
    language_code = SPEECHMATICS_LANG_TO_CODE[language]
    conf = {
        "type": "transcription",
        "transcription_config": {"language": language_code},
    }

    with speechmatics.client.BatchClient(settings) as client:
        try:
            job_id = client.submit_job(
                audio=audio_file,
                transcription_config=conf,
            )
            print(f"job {job_id} submitted successfully, waiting for transcript")

            transcript = client.wait_for_completion(job_id, transcription_format="txt")
            return transcript
        except Exception as e:
            raise e


def speechmatics_live_avr(api_key: str, audio_file: str, language: Language) -> str:
    language_code = SPEECHMATICS_LANG_TO_CODE[language]
    ws = speechmatics.client.WebsocketClient(
        speechmatics.models.ConnectionSettings(
            url=WS_API_URL,
            auth_token=api_key,
            generate_temp_token=True,
        )
    )

    transcript = []

    # Define an event handler when a full transcript is received
    def print_transcript(msg):
        transcript.append(msg["metadata"]["transcript"])

    ws.add_event_handler(
        event_name=speechmatics.models.ServerMessageType.AddTranscript,
        event_handler=print_transcript,
    )

    audio_settings = speechmatics.models.AudioSettings()
    conf = speechmatics.models.TranscriptionConfig(
        language=language_code,
        enable_partials=True,
        max_delay=2,
        max_delay_mode="fixed",
    )

    with open(audio_file, "rb") as fd:
        try:
            ws.run_synchronously(fd, conf, audio_settings)
        except Exception as e:
            raise e

    return "".join(transcript)
