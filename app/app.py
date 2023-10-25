import time

from flask import Flask, request, jsonify

from app import caching
from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.language import Language
from app.models import Conversation, ConversationParticipant, Message

# TODO: use more secure method of storing secret keys
from app.secret_keys import *
from app.tts.aws_polly import (
    create_polly_client,
    extract_file_name_from_output_uri,
    generate_presigned_url,
    polly_tts,
)
from app.translation.deepl import deepl_translate

app = Flask(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = caching.create_redis_client(REDIS_HOST, REDIS_PORT)
polly_client = create_polly_client(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)


@app.route("/")
def hello_world():
    resp = {"data": ["Hello World", "x", "y"]}
    return jsonify(resp)


@app.route("/new_conversation", methods=["POST"])
def new_conversation():
    params = request.get_json()
    content = params.get("content")
    user_lang = params.get("userLang")
    resp_lang = params.get("respLang")
    if content is None or user_lang is None or resp_lang is None:
        return jsonify(error="Missing parameter"), 400

    user_lang = Language(user_lang.lower())
    resp_lang = Language(resp_lang.lower())

    translation = deepl_translate(content, user_lang, resp_lang, DEEPL_API_KEY)

    combined_message = content + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[user_lang]
    combined_translation = translation + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[resp_lang]

    tts_uri = polly_tts(polly_client, combined_translation, resp_lang, "standard")
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=combined_message,
        translation=combined_translation,
        tts_uri=presigned_tts_url,
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

    conversation_dict = {
        "history": [
            {
                "content": "Hello everyone!\n\nI am using a translation app. Please speak into the phone when you respond",
                "sender": "user",
                "translation": "Bonjour \u00e0 tous!\n\nJ'utilise une application de traduction. Veuillez parler dans le t\u00e9l\u00e9phone lorsque vous r\u00e9pondez.",
                "tts_uri": "https://shuopolly.s3.amazonaws.com/tts.92d709b0-2c22-4db6-8d4a-2493704c1a7f.mp3?AWSAccessKeyId=AKIAUAUBZVHG5XLUVMHO&Signature=nzKLOQ23lg8VB5wkZ15dbOGixbw%3D&Expires=1698248159",
            }
        ],
        "id": "7c551128-cd87-4a81-af24-d89b946cc2fb",
        "intro_message": "I am using a translation app. Please speak into the phone when you respond",
        "resp_lang": "French",
        "user_lang": "English",
    }
    return jsonify(conversation_dict), 200


@app.route("/new_message", methods=["POST"])
def new_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    sender = params.get("sender")
    content = params.get("content")
    if conversation_id is None or sender is None or content is None:
        return jsonify(error="Missing parameter"), 400
    conversation_id = conversation_id.lower()
    sender = sender.lower()

    # only for user messages right now
    assert sender == "user"

    sender = ConversationParticipant(sender)
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    translation = deepl_translate(
        content, conversation.user_lang, conversation.resp_lang, DEEPL_API_KEY
    )

    tts_uri = polly_tts(polly_client, translation, conversation.resp_lang, "standard")
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=content,
        translation=translation,
        tts_uri=presigned_tts_url,
    )
    conversation.new_message(new_message)
    caching.save_conversation(redis_client, conversation)

    return jsonify(new_message.to_dict()), 200


@app.route("/test_new_message", methods=["POST"])
def test_new_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    sender = params.get("sender")
    content = params.get("content")
    print(conversation_id)
    print(sender)
    print(content)
    if conversation_id is None or content is None:
        return jsonify(error="Missing parameter"), 400
    conversation_id = conversation_id.lower()
    sender = sender.lower()

    sender = ConversationParticipant(sender)
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    new_message = Message(
        sender=ConversationParticipant.USER,
        content=content,
        translation="asdf",
        tts_uri="https://shuopolly.s3.amazonaws.com/tts.92d709b0-2c22-4db6-8d4a-2493704c1a7f.mp3?AWSAccessKeyId=AKIAUAUBZVHG5XLUVMHO&Signature=nzKLOQ23lg8VB5wkZ15dbOGixbw%3D&Expires=1698248159",
    )
    conversation.new_message(new_message)

    return jsonify(new_message.to_dict()), 200
