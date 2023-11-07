import json
import time

from flask import Response, request, jsonify, stream_with_context

from app.api import api_utils
from app.app import app, test_tts_object
from app.generative.openai_gpt import (
    OpenAIReponseOptionStreamDFA,
    parse_options_with_translations,
)
from app.models import ConversationParticipant, Message

# TODO: use more secure method of storing secret keys
from app.secret_keys import *
from app.tts.aws_polly import generate_presigned_url


@app.route("/")
def hello_world():
    resp = {"data": ["Hello World", "x", "y"]}
    return jsonify(resp)


@app.route("/test_new_conversation", methods=["POST"])
def test_new_conversation():
    params = request.get_json()
    content = params.get("content")
    user_lang = params.get("userLang")
    resp_lang = params.get("respLang")
    print("-" * 10)
    print("call test_new_conversation")
    print("content:", content)
    print("user_lang:", user_lang)
    print("resp_lang:", resp_lang)

    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, test_tts_object
    )

    conversation_dict = {
        "id": "a66e89f7-a440-4122-af1b-5cb67fd86c5c",
        "intro_message": "I am using a translation app. Please speak into the phone when you respond.",
        "history": [
            {
                "sender": "user",
                "content": "Excuse me, could you help me find the closest hospital?\n\nI am using a translation app. Please speak into the phone when you respond.",
                "translation": "Excusez-moi, pourriez-vous m'aider à trouver l'hôpital le plus proche ?\n\nJ'utilise une application de traduction. Veuillez parler dans le téléphone lorsque vous répondez.",
                "tts_uri": presigned_tts_url,
                "tts_task_id": "e0a6a1b2-e739-4c00-853d-67febd415da2",
            }
        ],
        "user_lang": "english",
        "resp_lang": "french",
    }
    return jsonify(conversation_dict), 200


@app.route("/test_new_user_message", methods=["POST"])
def test_new_user_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    content = params.get("content")
    print("-" * 10)
    print("call test_new_user_message")
    print("conversation_id:", conversation_id)
    print("content:", content)
    if conversation_id is None or content is None:
        return jsonify(error="Missing parameter"), 400
    conversation_id = conversation_id.lower()

    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, test_tts_object
    )

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=content,
        translation="asdf",
        tts_uri=presigned_tts_url,
        tts_task_id="asdf",
    )

    return jsonify(new_message.to_dict()), 200


@app.route("/test_new_resp_message", methods=["POST"])
def test_new_resp_message():
    conversation_id = request.form.get("conversationId")
    file = request.files.get("file")
    print("-" * 10)
    print("call test_new_resp_message")
    print("conversation_id:", conversation_id)
    print("filename:", file.filename)
    if conversation_id is None or file is None:
        return jsonify(error="Missing parameter"), 400
    if not api_utils.allowed_audio_file(file.filename):
        return jsonify(error="Invalid file name"), 400

    conversation_id = conversation_id.lower()

    api_utils.save_resp_audio(file, file.filename)

    time.sleep(3)

    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, test_tts_object
    )

    new_message = Message(
        sender=ConversationParticipant.RESPONDENT,
        content="你受伤了吗？",
        translation="Are you hurt?",
        tts_uri=presigned_tts_url,
        tts_task_id="asdf",
    )

    return jsonify(new_message.to_dict()), 200


@app.route("/test_response_options", methods=["POST"])
def test_response_options():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    print("-" * 10)
    print("call test_response_options")
    print("conversation_id:", conversation_id)
    if conversation_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()

    # time.sleep(3)
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

    return jsonify(api_utils.format_response_options(options)), 200


@app.route("/test_response_options_stream", methods=["GET"])
def test_response_options_stream():
    response_content = """
<Start>
"I'm going to Amsterdam."
<End>
<Start>
"I haven't decided on the exact city yet."
<End>
<Start>
"My destination is Rotterdam."
<End>
"""

    parser = OpenAIReponseOptionStreamDFA()

    def generate(prompt):
        for char in response_content:
            chunk = {
                "id": "chatcmpl-8APG8TCIjRjUaGDR5XzDwT2UXl9OT",
                "object": "chat.completion.chunk",
                "created": 1697491068,
                "model": "gpt-3.5-turbo-0613",
                "choices": [
                    {"index": 0, "delta": {"content": char}, "finish_reason": "null"}
                ],
            }

            events = parser.process_chunk(chunk)
            for event in events:
                print(json.dumps(event))
                yield f"data: {json.dumps(event)}\n\n"
            time.sleep(0.05)

        print("".join(parser.response_chars))
        for start_idx, end_idx in parser.message_idx:
            print("".join(parser.response_chars[start_idx:end_idx]))

    conversation_id = request.args.get("conversationId")
    if conversation_id is None:
        return jsonify(error="Missing parameter"), 400
    print("-" * 10)
    print("call test_response_options_stream")
    print("conversation_id:", conversation_id)

    return Response(stream_with_context(generate("")), content_type="text/event-stream")
