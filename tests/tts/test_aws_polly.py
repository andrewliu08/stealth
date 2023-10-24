import datetime

import pytest

from app.tts.aws_polly import (
    extract_file_name_from_output_uri,
    extract_uri_from_polly_response,
)


@pytest.fixture
def synthesis_task_response():
    return {
        "ResponseMetadata": {
            "RequestId": "86fdeea4-1561-41da-9af3-3f8cb0cb4f30",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "x-amzn-requestid": "86fdeea4-1561-41da-9af3-3f8cb0cb4f30",
                "content-type": "application/json",
                "content-length": "501",
                "date": "Sat, 21 Oct 2023 23:46:52 GMT",
            },
            "RetryAttempts": 0,
        },
        "SynthesisTask": {
            "Engine": "standard",
            "TaskId": "9c1e400f-9206-4973-8ff8-65bb34052dec",
            "TaskStatus": "scheduled",
            "OutputUri": "https://s3.us-east-1.amazonaws.com/shuopolly/test.9c1e400f-9206-4973-8ff8-65bb34052dec.mp3",
            "CreationTime": datetime.datetime(2023, 10, 21, 19, 46, 52, 668000),
            "RequestCharacters": 5,
            "OutputFormat": "mp3",
            "TextType": "text",
            "VoiceId": "Matthew",
        },
    }


def test_extract_uri_from_polly_response(synthesis_task_response):
    output_uri = extract_uri_from_polly_response(synthesis_task_response)
    assert (
        output_uri
        == "https://s3.us-east-1.amazonaws.com/shuopolly/test.9c1e400f-9206-4973-8ff8-65bb34052dec.mp3"
    )


def test_extract_file_name_from_output_uri(synthesis_task_response):
    output_uri = extract_uri_from_polly_response(synthesis_task_response)
    file_name = extract_file_name_from_output_uri(output_uri)
    assert file_name == "test.9c1e400f-9206-4973-8ff8-65bb34052dec.mp3"
