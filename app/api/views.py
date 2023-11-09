import json

from flask import Response, request, jsonify, stream_with_context

from app import caching
from app.api import api_utils
from app.app import app, redis_client, polly_client
from app.avr.speechmatics import speechmatics_live_avr
from app.constants.fixed_response_options import FIXED_RESPONSE_OPTIONS
from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.starter_messages import STARTER_MESSAGE_TRANSLATIONS
from app.generative.prompts import get_prompt, get_prompt_with_translations
from app.generative.openai_gpt import (
    OpenAIReponseOptionStreamDFA,
    extract_message_from_openai_response,
    gpt_responses,
    parse_options_with_translations,
    set_api_key,
)
from app.models import Conversation, ConversationParticipant, Message

# TODO: use more secure method of storing secret keys
from app.secret_keys import *
from app.translation.deepl import deepl_translate
from app.tts.aws_polly import (
    extract_file_name_from_output_uri,
    extract_task_id_from_polly_response,
    extract_uri_from_polly_response,
    generate_presigned_url,
    polly_synthesis_task_status,
    polly_tts,
)


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
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        id=caching.create_id(),
        sender=ConversationParticipant.USER,
        content=combined_message,
        translation=combined_translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation = Conversation(
        id=caching.create_id(),
        intro_message=INTRO_MESSAGE_TRANSLATIONS[user_lang],
        history=[new_message],
        user_lang=user_lang,
        resp_lang=resp_lang,
    )
    caching.save_conversation(redis_client, conversation)

    return jsonify(conversation.to_dict()), 200


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
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        id=caching.create_id(),
        sender=ConversationParticipant.USER,
        content=content,
        translation=translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation.new_message(new_message)
    caching.save_conversation(redis_client, conversation)

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
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, file_name
    )

    new_message = Message(
        id=caching.create_id(),
        sender=ConversationParticipant.RESPONDENT,
        content=transcript,
        translation=translation,
        tts_uri=presigned_tts_url,
        tts_task_id=tts_task_id,
    )
    conversation.new_message(new_message)
    caching.save_conversation(redis_client, conversation)

    return jsonify(new_message.to_dict()), 200


@app.route("/delete_message", methods=["POST"])
def delete_message():
    params = request.get_json()
    conversation_id = params.get("conversationId")
    message_id = params.get("messageId")
    if conversation_id is None or message_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()
    message_id = message_id.lower()
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    successfully_deleted = conversation.delete_message(message_id)
    if not successfully_deleted:
        return jsonify(error="Message not found"), 404
    caching.save_conversation(redis_client, conversation)

    return jsonify({}), 200


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

    prompt = get_prompt_with_translations(conversation, num_response_options=3)
    print(prompt)
    set_api_key(OPENAI_API_KEY)
    response = gpt_responses(prompt, stream=False)
    gpt_message = extract_message_from_openai_response(response)
    print(gpt_message)
    options = parse_options_with_translations(gpt_message)

    return jsonify(api_utils.format_response_options(options)), 200


@app.route("/response_options_stream", methods=["GET"])
def response_options_stream():
    conversation_id = request.args.get("conversationId")
    if conversation_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404

    def generate(prompt):
        for response in FIXED_RESPONSE_OPTIONS[conversation.user_lang]:
            response_event = {"event": "message", "data": response}
            end_event = {"event": "end"}
            yield f"data: {json.dumps(response_event)}\n\n"
            yield f"data: {json.dumps(end_event)}\n\n"

        response_stream = gpt_responses(prompt, stream=True)
        parser = OpenAIReponseOptionStreamDFA()
        for chunk in response_stream:
            events = parser.process_chunk(chunk)
            for event in events:
                yield f"data: {json.dumps(event)}\n\n"

        print("".join(parser.response_chars))
        for start_idx, end_idx in parser.message_idx:
            print("".join(parser.response_chars[start_idx:end_idx]))

    prompt = get_prompt(conversation, num_response_options=3)
    print(prompt)
    set_api_key(OPENAI_API_KEY)

    return Response(
        stream_with_context(generate(prompt)), content_type="text/event-stream"
    )
