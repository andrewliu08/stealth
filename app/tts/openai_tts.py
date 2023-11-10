import os
import time

from openai import OpenAI


def openai_tts(openai_client: OpenAI, text: str):
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    return response
