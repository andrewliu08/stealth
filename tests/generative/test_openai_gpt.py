import pytest

from app.generative.openai_gpt import (
    OpenAIReponseOptionStreamDFA,
    extract_message_from_openai_response,
    extract_message_from_openai_response_chunk,
    extract_stop_reason_from_openai_response_chunk,
    parse_options,
    parse_options_with_translations,
)


@pytest.fixture
def openai_response():
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo-0613",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "\n\nHello there, how may I assist you today?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
    }


@pytest.fixture
def openai_response_chunk():
    return {
        "id": "chatcmpl-8APG8TCIjRjUaGDR5XzDwT2UXl9OT",
        "object": "chat.completion.chunk",
        "created": 1697491068,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {"index": 0, "delta": {"content": "Option"}, "finish_reason": "null"}
        ],
    }


def convert_to_response_chunk(message):
    return {
        "id": "chatcmpl-8APG8TCIjRjUaGDR5XzDwT2UXl9OT",
        "object": "chat.completion.chunk",
        "created": 1697491068,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {"index": 0, "delta": {"content": message}, "finish_reason": "null"}
        ],
    }


def test_stream_dfa_process_chars():
    message = """
<Start>
"Thank you for the recommendation. What type of cuisine do they serve at "au noir"?"
<End>
<Start>
"Do they have any vegetarian options at 'au noir'? I have dietary restrictions."
<End>
<Start>
"Is <au noir> within walking distance from here?"
<End>
"""
    chunks = list(message)
    parser = OpenAIReponseOptionStreamDFA()
    events = []
    for chunk in chunks:
        event = parser.process_char(chunk)
        events.append(event)

    messages = []
    curr_message = []
    for event in events:
        if "event" not in event:
            continue
        if event["event"] == "message":
            curr_message += event["data"]
        elif event["event"] == "end":
            messages.append("".join(curr_message))
            curr_message = []

    expected_messages = [
        'Thank you for the recommendation. What type of cuisine do they serve at "au noir"?',
        "Do they have any vegetarian options at 'au noir'? I have dietary restrictions.",
        "Is <au noir> within walking distance from here?",
    ]
    assert messages == expected_messages


def test_parse_options():
    response_content = """Option 1:
"I'm going to Amsterdam."

Option 2:
"I haven't decided on the exact city yet."

Option 3:
"My destination is Rotterdam."
"""

    options = parse_options(response_content)
    assert options == [
        "I'm going to Amsterdam.",
        "I haven't decided on the exact city yet.",
        "My destination is Rotterdam.",
    ]


def test_parse_options_with_translations():
    response_content = """Option 1:
"Je vais à Amsterdam."
"I'm going to Amsterdam."

Option 2:
"Je n'ai pas encore décidé de la ville exacte."
"I haven't decided on the exact city yet."

Option 3:
"Ma destination est Rotterdam."
"My destination is Rotterdam."
"""

    options = parse_options_with_translations(response_content)
    assert options == [
        (
            "Je vais à Amsterdam.",
            "I'm going to Amsterdam.",
        ),
        (
            "Je n'ai pas encore décidé de la ville exacte.",
            "I haven't decided on the exact city yet.",
        ),
        (
            "Ma destination est Rotterdam.",
            "My destination is Rotterdam.",
        ),
    ]


def test_extract_message_from_openai_response(openai_response):
    message = extract_message_from_openai_response(openai_response)
    assert message == "\n\nHello there, how may I assist you today?"


def test_extract_message_from_openai_response_chunk(openai_response_chunk):
    message = extract_message_from_openai_response_chunk(openai_response_chunk)
    assert message == "Option"


def test_extract_stop_reason_from_openai_response_chunk(openai_response_chunk):
    stop_reason = extract_stop_reason_from_openai_response_chunk(openai_response_chunk)
    assert stop_reason == "null"
