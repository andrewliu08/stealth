import os
import time
from typing import List, Tuple

from flask import Flask, request, jsonify

from app import caching
from app.api import api_utils
from app.app import app, redis_client, polly_client, test_tts_object
from app.avr.speechmatics import speechmatics_live_avr
from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.starter_messages import STARTER_MESSAGE_TRANSLATIONS
from app.generative.prompts import get_prompt
from app.generative.openai_gpt import (
    extract_message_from_openai_response,
    gpt_responses,
    parse_options,
    set_api_key,
)
from app.models import Conversation, ConversationParticipant, Message

# TODO: use more secure method of storing secret keys
from app.secret_keys import *
from app.translation.deepl import deepl_translate
from app.tts.aws_polly import (
    extract_file_name_from_output_uri,
    extract_task_id_from_polly_respnonse,
    extract_uri_from_polly_response,
    generate_presigned_url,
    polly_synthesis_task_status,
    polly_tts,
)


@app.route("/")
def hello_world():
    resp = {"data": ["Hello World", "x", "y"]}
    return jsonify(resp)


@app.route("/starter_messages", methods=["GET"])
def starter_messages():
    lang = request.args.get("lang")
    if lang is None:
        return jsonify(error="Missing parameter"), 400

    try:
        lang = api_utils.parse_language(lang)
        messages = STARTER_MESSAGE_TRANSLATIONS[lang]
    except ValueError:
        return jsonify(error="Invalid language"), 400

    return jsonify({"starter_messages": messages}), 200


@app.route("/tts_task_status", methods=["POST"])
def tts_task_status():
    params = request.get_json()
    task_id = params.get("taskId")
    if task_id is None:
        return jsonify(error="Missing parameter"), 400

    task_status = polly_synthesis_task_status(polly_client, task_id)
    return jsonify({"status": task_status}), 200


@app.route("/new_conversation", methods=["POST"])
def new_conversation():
    params = request.get_json()
    content = params.get("content")
    user_lang = params.get("userLang")
    resp_lang = params.get("respLang")
    if content is None or user_lang is None or resp_lang is None:
        return jsonify(error="Missing parameter"), 400

    try:
        user_lang = api_utils.parse_language(user_lang)
        resp_lang = api_utils.parse_language(resp_lang)
    except ValueError:
        return jsonify(error="Invalid language"), 400

    translation = deepl_translate(content, user_lang, resp_lang, DEEPL_API_KEY)

    combined_message = content + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[user_lang]
    combined_translation = translation + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[resp_lang]

    polly_response = polly_tts(
        polly_client, combined_translation, resp_lang, "standard"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_respnonse(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=combined_message,
        translation=combined_translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation = Conversation(
        id=caching.create_conversation_id(),
        intro_message=INTRO_MESSAGE_TRANSLATIONS[user_lang],
        history=[new_message],
        user_lang=user_lang,
        resp_lang=resp_lang,
    )
    caching.save_conversation(redis_client, conversation)

    return jsonify(conversation.to_dict()), 200


@app.route("/test_new_conversation", methods=["POST"])
def test_new_conversation():
    params = request.get_json()
    content = params.get("content")
    user_lang = params.get("userLang")
    resp_lang = params.get("respLang")
    print(content)
    print(user_lang)
    print(resp_lang)

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


@app.route("/new_user_message", methods=["POST"])
def new_user_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    content = params.get("content")
    if conversation_id is None or content is None:
        return jsonify(error="Missing parameter"), 400
    conversation_id = conversation_id.lower()

    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    translation = deepl_translate(
        content, conversation.user_lang, conversation.resp_lang, DEEPL_API_KEY
    )

    polly_response = polly_tts(
        polly_client, translation, conversation.resp_lang, "standard"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_respnonse(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=content,
        translation=translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation.new_message(new_message)
    caching.save_conversation(redis_client, conversation)

    return jsonify(new_message.to_dict()), 200


@app.route("/test_new_user_message", methods=["POST"])
def test_new_user_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    content = params.get("content")
    print("conversation_id:", conversation_id)
    print("content:", content)
    if conversation_id is None or content is None:
        return jsonify(error="Missing parameter"), 400
    conversation_id = conversation_id.lower()

    # conversation = caching.get_conversation(redis_client, conversation_id)
    # if conversation is None:
    #     return jsonify(error="Conversation not found"), 404

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
    # conversation.new_message(new_message)

    return jsonify(new_message.to_dict()), 200


@app.route("/test_new_resp_message", methods=["POST"])
def test_new_resp_message():
    conversation_id = request.form.get("conversationId")
    file = request.files.get("file")
    if conversation_id is None or file is None:
        return jsonify(error="Missing parameter"), 400
    if not api_utils.allowed_audio_file(file.filename):
        return jsonify(error="Invalid file name"), 400

    conversation_id = conversation_id.lower()
    # conversation = caching.get_conversation(redis_client, conversation_id)
    # if conversation is None:
    #     return jsonify(error="Conversation not found"), 404

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
    # conversation.new_message(new_message)
    # caching.save_conversation(redis_client, conversation)

    return jsonify(new_message.to_dict()), 200


@app.route("/new_resp_message", methods=["POST"])
def new_resp_message():
    conversation_id = request.form.get("conversationId")
    file = request.files.get("file")
    if conversation_id is None or file is None:
        return jsonify(error="Missing parameter"), 400
    if not api_utils.allowed_audio_file(file.filename):
        return jsonify(error="Invalid file name"), 400

    conversation_id = conversation_id.lower()
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    file_path = api_utils.save_resp_audio(file, conversation_id + "_" + file.filename)

    transcript = speechmatics_live_avr(
        SPEECHMATICS_API_KEY, conversation.resp_lang, file_path
    )

    translation = deepl_translate(
        transcript, conversation.resp_lang, conversation.user_lang, DEEPL_API_KEY
    )

    polly_response = polly_tts(
        polly_client, translation, conversation.user_lang, "standard"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_respnonse(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        sender=ConversationParticipant.RESPONDENT,
        content=transcript,
        translation=translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation.new_message(new_message)
    caching.save_conversation(redis_client, conversation)

    return jsonify(new_message.to_dict()), 200


@app.route("/response_options", methods=["POST"])
def response_options():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    if conversation_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    prompt = get_prompt(conversation, num_response_options=3)
    print(prompt)
    set_api_key(OPENAI_API_KEY)
    response = gpt_responses(prompt, stream=False)
    gpt_message = extract_message_from_openai_response(response)
    print(gpt_message)
    options = parse_options(gpt_message)

    return jsonify(api_utils.format_response_options(options)), 200


@app.route("/test_response_options", methods=["POST"])
def test_response_options():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    if conversation_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()
    # conversation = caching.get_conversation(redis_client, conversation_id)
    # if conversation is None:
    #     return jsonify(error="Conversation not found"), 404

    # prompt = get_prompt(conversation, num_response_options=3)
    # print("prompt:", prompt)
    time.sleep(3)
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
    options = parse_options(response_content)

    return jsonify(api_utils.format_response_options(options)), 200


@app.route("/test", methods=["POST"])
def test():
    conversation_id = request.form.get("conversationId")
    print("conversation_id:", conversation_id)
    return jsonify({"conversation_id": conversation_id}), 200


@app.route("/upload", methods=["POST"])
def upload_file():
    print("Hi")
    print("request.files", request.files)
    print("request.form", request.form)
    conversation_id = request.form.get("conversationId")
    print("conversation_id:", conversation_id)
    if "file" not in request.files:
        return "No file part", 400

    print("Has file part")

    file = request.files["file"]
    if file is None:
        return "No selected file", 401
    print("has selected file")
    print(file.filename)
    if not api_utils.allowed_audio_file(file.filename):
        return "Invalid file name", 401
    print("valid file name")

    file.save(os.path.join("temp", file.filename))
    return jsonify({"conversation_id": "asdf"}), 200
