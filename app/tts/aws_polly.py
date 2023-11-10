import os
from typing import Any, Dict

import boto3

from app.constants.language import Language


# https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
AWS_POLLY_LANG_TO_VOICE: Dict[Language, str] = {
    Language.ARABIC: "Zeina",
    Language.CANTONESE: "Hiujin",
    Language.CATALAN: "Lisa",
    Language.DANISH: "Mads",
    Language.DUTCH: "Ruben",
    Language.ENGLISH: "Matthew",
    Language.FINNISH: "Suvi",
    Language.FRENCH: "Lea",
    Language.GERMAN: "Hans",
    Language.HINDI: "Aditi",
    Language.ICELANDIC: "Karl",
    Language.ITALIAN: "Giorgio",
    Language.JAPANESE: "Takumi",
    Language.KOREAN: "Seoyeon",
    Language.MANDARIN: "Zhiyu",
    Language.NORWEGIAN: "Liv",
    Language.POLISH: "Jan",
    Language.PORTUGUESE: "Cristiano",
    Language.ROMANIAN: "Carmen",
    Language.RUSSIAN: "Maxim",
    Language.SPANISH: "Enrique",
    Language.SWEDISH: "Astrid",
    Language.TURKISH: "Filiz",
    Language.WELSH: "Gwyneth",
}


def extract_task_id_from_polly_response(response: Dict[str, Any]) -> str:
    task_id = response["SynthesisTask"]["TaskId"]
    return task_id


def extract_uri_from_polly_response(response: Dict[str, Any]) -> str:
    output_uri = response["SynthesisTask"]["OutputUri"]
    return output_uri


def extract_file_name_from_output_uri(output_uri: str) -> str:
    return output_uri.split("/")[-1]


def polly_tts(
    polly_client: boto3.client,
    text: str,
    language: Language,
    engine: str,
) -> str:
    """
    Create an AWS Polly speech synthesis task that does TTS for the
    given text. The output file is saved to AWS S3. The file name is
    returned.

    engine can either be "standard" or "neural"
    """
    # voice_id is used to select the language and voice.
    voice_id = AWS_POLLY_LANG_TO_VOICE[language]

    response = polly_client.start_speech_synthesis_task(
        VoiceId=voice_id,
        Engine=engine,
        OutputS3BucketName=os.environ.get("SHUO_TTS_BUCKET_NAME"),
        OutputS3KeyPrefix="polly",
        OutputFormat="mp3",
        Text=text,
    )

    return response


def polly_synthesis_task_status(polly_client: boto3.client, task_id: str) -> str:
    task_check = polly_client.get_speech_synthesis_task(TaskId=task_id)
    task_status = task_check["SynthesisTask"]["TaskStatus"]
    return task_status
