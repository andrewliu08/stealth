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


@app.route("/translate", methods=["POST"])
def translate():
    message = request.form.get("message")
    source_lang = request.form.get("source_lang")
    target_lang = request.form.get("target_lang")
    if message is None or source_lang is None or target_lang is None:
        return jsonify(error="Message parameter is required"), 400

    source_lang = Language(source_lang)
    target_lang = Language(target_lang)
    res = deepl_translate(message, source_lang, target_lang, DEEPL_API_KEY)
    translation = res.json()["translations"][0]["text"]

    resp = {"translation": translation}
    return jsonify(resp), 200


@app.route("/new_conversation", methods=["POST"])
def new_conversation():
    message = request.form.get("message")
    intro = request.form.get("intro")
    user_lang = request.form.get("user_lang")
    resp_lang = request.form.get("resp_lang")
    if message is None or intro is None or user_lang is None or resp_lang is None:
        return jsonify(error="Missing parameter"), 400

    user_lang = Language(user_lang)
    resp_lang = Language(resp_lang)

    translation_resp = deepl_translate(message, user_lang, resp_lang, DEEPL_API_KEY)
    translation = translation_resp.json()["translations"][0]["text"]

    combined_message = message + "\n\n" + intro
    combined_translation = translation + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[resp_lang]

    tts_uri = polly_tts(polly_client, combined_translation, resp_lang, "standard")
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    conversation = Conversation(
        id=caching.create_conversation_id(),
        intro_message=intro,
        history=[
            Message(
                sender=ConversationParticipant.USER,
                content=combined_message,
                translation=combined_translation,
                tts_uri=presigned_tts_url,
            )
        ],
        user_lang=user_lang,
        resp_lang=resp_lang,
    )
    caching.new_conversation(redis_client, conversation)

    resp = {"conversation": conversation.to_dict()}
    return jsonify(resp), 200


@app.route("/test_new_conversation", methods=["GET"])
def test_new_conversation():
    conversation_dict = {
        "conversation": {
            "history": [
                {
                    "content": "hello everyone\n\nI am using a translation app. Please speak into the phone when you respond",
                    "sender": "user",
                    "translation": "Bonjour \u00e0 tous\n\nJ'utilise une application de traduction. Veuillez parler dans le t\u00e9l\u00e9phone lorsque vous r\u00e9pondez.",
                    "tts_uri": "https://shuopolly.s3.amazonaws.com/tts.92d709b0-2c22-4db6-8d4a-2493704c1a7f.mp3?AWSAccessKeyId=AKIAUAUBZVHG5XLUVMHO&Signature=nzKLOQ23lg8VB5wkZ15dbOGixbw%3D&Expires=1698248159",
                }
            ],
            "id": "7c551128-cd87-4a81-af24-d89b946cc2fb",
            "intro_message": "I am using a translation app. Please speak into the phone when you respond",
            "resp_lang": "French",
            "user_lang": "English",
        }
    }
    return jsonify(conversation_dict), 200
