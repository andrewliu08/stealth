import pytest
from openai.types.chat.chat_completion import ChatCompletion, Choice as ChatChoice
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice as ChunkChoice,
    ChoiceDelta,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

# from openai.types import Choice

from app.generative.openai_gpt import (
    OpenAIReponseOptionStreamDFA,
    extract_message_from_openai_response,
    extract_message_from_openai_response_chunk,
    extract_finish_reason_from_openai_response_chunk,
    parse_options,
    parse_options_with_translations,
    parse_streamed_options,
)


@pytest.fixture
def openai_response():
    return ChatCompletion(
        id="chatcmpl-8J7nRQFmcjrcwkES2iXH6irGlBOM1",
        choices=[
            ChatChoice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Hello world",
                    role="assistant",
                    function_call=None,
                    tool_calls=None,
                ),
            )
        ],
        created=1699568893,
        model="gpt-3.5-turbo-0613",
        object="chat.completion",
        system_fingerprint=None,
        usage=CompletionUsage(completion_tokens=16, prompt_tokens=11, total_tokens=27),
    )


@pytest.fixture
def openai_response_chunk():
    return ChatCompletionChunk(
        id="chatcmpl-8J7mnNeFwHVJxH9Pw0MEdSg1hgdOF",
        choices=[
            ChunkChoice(
                delta=ChoiceDelta(
                    content="Hello", function_call=None, role=None, tool_calls=None
                ),
                finish_reason=None,
                index=0,
            )
        ],
        created=1699568853,
        model="gpt-3.5-turbo-0613",
        object="chat.completion.chunk",
        system_fingerprint=None,
    )


def convert_to_response_chunk(message):
    return ChatCompletionChunk(
        id="chatcmpl-8J7mnNeFwHVJxH9Pw0MEdSg1hgdOF",
        choices=[
            ChunkChoice(
                delta=ChoiceDelta(
                    content=message, function_call=None, role=None, tool_calls=None
                ),
                finish_reason=None,
                index=0,
            )
        ],
        created=1699568853,
        model="gpt-3.5-turbo-0613",
        object="chat.completion.chunk",
        system_fingerprint=None,
    )


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


def test_stream_dfa_process_chars_with_triple_quotes():
    message = '''
"""
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
'''
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


def test_parse_streamed_options():
    response_content = '''"""<Start>
"Can you tell me the nearest metro station to Musee d'Orsay?"
<End>
<Start>
"What are the museum's opening hours?"
<End>
<Start>
"Is there an entrance fee to Musee d'Orsay?"
<End>
"""
'''
    options = parse_streamed_options(response_content)
    assert options == [
        "Can you tell me the nearest metro station to Musee d'Orsay?",
        "What are the museum's opening hours?",
        "Is there an entrance fee to Musee d'Orsay?",
    ]


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
    assert message == "Hello world"


def test_extract_message_from_openai_response_chunk(openai_response_chunk):
    message = extract_message_from_openai_response_chunk(openai_response_chunk)
    assert message == "Hello"


def test_extract_stop_reason_from_openai_response_chunk(openai_response_chunk):
    stop_reason = extract_finish_reason_from_openai_response_chunk(
        openai_response_chunk
    )
    assert stop_reason is None
