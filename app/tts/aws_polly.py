from typing import Any, Dict

import boto3

from app.constants.language import Language

AWS_POLLY_LANG_TO_VOICE: Dict[Language, str] = {
    Language.ENGLISH: "Matthew",
    Language.FRENCH: "Lea",
    Language.MANDARIN: "Zhiyu",
}

SAVED_POLLY_OUTPUT_BUCKET_NAME = "shuopolly"
SAVED_POLLY_OUTPUT_BUCKET_REGION = "us-east-1"


def create_polly_client(
    aws_access_key_id: str, aws_secret_access_key: str
) -> boto3.client:
    return boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=SAVED_POLLY_OUTPUT_BUCKET_REGION,
    ).client("polly")


def extract_task_id_from_polly_respnonse(response: Dict[str, Any]) -> str:
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
        OutputS3BucketName=SAVED_POLLY_OUTPUT_BUCKET_NAME,
        OutputS3KeyPrefix="tts",
        OutputFormat="mp3",
        Text=text,
    )

    return response


def polly_synthesis_task_status(polly_client: boto3.client, task_id: str) -> str:
    task_check = polly_client.get_speech_synthesis_task(TaskId=task_id)
    task_status = task_check["SynthesisTask"]["TaskStatus"]
    return task_status


def generate_presigned_url(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    object_name: str,
    expires_in=86400,
) -> str:
    # TODO: pre-create and save the s3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=SAVED_POLLY_OUTPUT_BUCKET_REGION,
    )
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": SAVED_POLLY_OUTPUT_BUCKET_NAME, "Key": object_name},
        ExpiresIn=expires_in,
    )
    return url
