import os

from openai import OpenAI


def create_openai_client(openai_api_key: str) -> OpenAI:
    client = OpenAI(api_key=openai_api_key)
    return client
