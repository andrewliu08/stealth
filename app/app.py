import time

from flask import Flask, request, jsonify

from app import caching
from app.language import Language
from app.models import Conversation, Message

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
    t = time.time()

    message = request.form.get("message")
    intro = request.form.get("intro")
    user_lang = request.form.get("user_lang")
    resp_lang = request.form.get("resp_lang")
    if message is None or intro is None or user_lang is None or resp_lang is None:
        return jsonify(error="Message parameter is required"), 400

    user_lang = Language(user_lang)
    resp_lang = Language(resp_lang)

    translation_resp = deepl_translate(message, user_lang, resp_lang, DEEPL_API_KEY)
    translation = translation_resp.json()["translations"][0]["text"]
    t1 = time.time()

    tts_uri = polly_tts(polly_client, translation, resp_lang, "standard")
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )
    t2 = time.time()

    conversation = Conversation(
        id=caching.create_conversation_id(),
        history=[
            Message(
                content=message, translation=translation, translation_tts_uri=tts_uri
            )
        ],
        user_lang=user_lang,
        resp_lang=resp_lang,
    )
    caching.new_conversation(redis_client, conversation)

    t3 = time.time()

    print("Translation time: {}".format(t1 - t))
    print("Redis time: {}".format(t2 - t1))

    # TODO: return presigned_tts_url
    resp = {"conversation": conversation.to_dict()}
    return jsonify(resp), 200
