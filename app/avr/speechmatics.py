from typing import Dict

import speechmatics

from app.constants.language import Language

# https://docs.speechmatics.com/introduction/supported-languages
SPEECHMATICS_LANG_TO_CODE: Dict[Language, str] = {
    Language.ENGLISH: "en",
    Language.FRENCH: "fr",
    Language.MANDARIN: "cmn",
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
    language: Language,
    audio_file: str,
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


def speechmatics_live_avr(api_key: str, language: Language, audio_file: str) -> str:
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
