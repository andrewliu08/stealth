import json
import os

from flask import Response, request, jsonify, stream_with_context

from app import caching
from app.api import api_utils
from app.app import app, openai_client, polly_client, redis_client, s3_client
from app.avr.openai_whisper import openai_avr
from app.avr.speechmatics import speechmatics_live_avr
from app.constants.fixed_response_options import FIXED_RESPONSE_OPTIONS
from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.starter_messages import STARTER_MESSAGE_TRANSLATIONS
from app.generative.prompts import get_prompt, get_prompt_with_translations
from app.generative.openai_gpt import (
    OpenAIReponseOptionStreamDFA,
    extract_finish_reason_from_openai_response_chunk,
    extract_message_from_openai_response,
    extract_message_from_openai_response_chunk,
    gpt_responses,
    parse_options_with_translations,
    parse_streamed_options,
)
from app.models import Conversation, ConversationParticipant, Message

from app.translation.deepl import deepl_translate
from app.tts.aws_polly import (
    extract_file_name_from_output_uri,
    extract_task_id_from_polly_response,
    extract_uri_from_polly_response,
    polly_synthesis_task_status,
    polly_tts,
)
from app.tts.openai_tts import openai_tts
from app.utils.aws_utils import generate_presigned_url


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


@app.route("/stream_tts", methods=["GET"])
def stream_tts():
    conversation_id = request.args.get("conversationId")
    message_id = request.args.get("messageId")
    if conversation_id is None or message_id is None:
        return jsonify(error="Missing parameter"), 400

    conversation_id = conversation_id.lower()
    message_id = message_id.lower()
    conversation = caching.get_conversation(redis_client, conversation_id)
    if conversation is None:
        return jsonify(error="Conversation not found"), 404
    message = conversation.get_message(message_id)
    if message is None:
        return jsonify(error="Message not found"), 404

    response = openai_tts(openai_client, message.translation)

    def generate():
        # 4096 bytes (or 4 KB) is a conventional one based on common I/O operations
        # and many OS use a 4 KB memory page size.
        for chunk in response.iter_bytes(chunk_size=4096):
            yield chunk

    return Response(generate(), mimetype="audio/mpeg")


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

    translation = deepl_translate(
        content, user_lang, resp_lang, os.environ.get("DEEPL_API_KEY")
    )

    combined_message = content + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[user_lang]
    combined_translation = translation + "\n\n" + INTRO_MESSAGE_TRANSLATIONS[resp_lang]

    polly_response = polly_tts(
        polly_client, combined_translation, resp_lang, "standard"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        s3_client,
        object_name=file_name,
        bucket_name=os.environ.get("SHUO_TTS_BUCKET_NAME"),
        expires_in=3600,
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
        content,
        conversation.user_lang,
        conversation.resp_lang,
        os.environ.get("DEEPL_API_KEY"),
    )

    polly_response = polly_tts(
        polly_client, translation, conversation.resp_lang, "standard"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        s3_client,
        object_name=file_name,
        bucket_name=os.environ.get("SHUO_TTS_BUCKET_NAME"),
        expires_in=3600,
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

    transcript = openai_avr(openai_client, file_path, conversation.resp_lang)
    transcript = transcript.strip()

    translation = deepl_translate(
        transcript,
        conversation.resp_lang,
        conversation.user_lang,
        os.environ.get("DEEPL_API_KEY"),
    )

    polly_response = polly_tts(
        polly_client, translation, conversation.user_lang, "neural"
    )
    tts_uri = extract_uri_from_polly_response(polly_response)
    tts_task_id = extract_task_id_from_polly_response(polly_response)
    file_name = extract_file_name_from_output_uri(tts_uri)
    presigned_tts_url = generate_presigned_url(
        s3_client,
        object_name=file_name,
        bucket_name=os.environ.get("SHUO_TTS_BUCKET_NAME"),
        expires_in=3600,
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

    prompt = get_prompt(conversation, num_response_options=3)
    print(prompt)

    def generate():
        for response in FIXED_RESPONSE_OPTIONS[conversation.user_lang]:
            response_event = {"event": "message", "data": response}
            end_event = {"event": "end"}
            yield f"data: {json.dumps(response_event)}\n\n"
            yield f"data: {json.dumps(end_event)}\n\n"

        response_stream = gpt_responses(openai_client, prompt, stream=True)
        parser = OpenAIReponseOptionStreamDFA()
        deltas = []
        parsing_error = True
        for chunk in response_stream:
            try:
                events = parser.process_chunk(chunk)
            except Exception as e:
                print("Error parsing GPT response stream:", e)
                events = []
                parsing_error = True

            for event in events:
                yield f"data: {json.dumps(event)}\n\n"

            if extract_finish_reason_from_openai_response_chunk(chunk) != "stop":
                message_chunk = extract_message_from_openai_response_chunk(chunk)
                deltas.append(message_chunk)

        full_message = "".join(deltas)
        print(full_message)

        # Parsing the whole response is more robust than parsing the stream
        if parsing_error:
            print("Parsing error, trying to recover...")

            # Tell app to clear the response options
            clear_event = {"event": "clear"}
            yield f"data: {json.dumps(clear_event)}\n\n"

            # Resend the fixed response options
            for response in FIXED_RESPONSE_OPTIONS[conversation.user_lang]:
                response_event = {"event": "message", "data": response}
                end_event = {"event": "end"}
                yield f"data: {json.dumps(response_event)}\n\n"
                yield f"data: {json.dumps(end_event)}\n\n"

            # Parse the full response
            options = parse_streamed_options(full_message)
            print(options)
            for option in options:
                response_event = {"event": "message", "data": option}
                end_event = {"event": "end"}
                yield f"data: {json.dumps(response_event)}\n\n"
                yield f"data: {json.dumps(end_event)}\n\n"

            stop_event = {"event": "stop"}
            yield f"data: {json.dumps(stop_event)}\n\n"
        else:
            for start_idx, end_idx in parser.message_idx:
                print("".join(parser.response_chars[start_idx:end_idx]))

    return Response(stream_with_context(generate()), content_type="text/event-stream")
