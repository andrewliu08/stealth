from typing import List, Tuple

import openai


def set_api_key(api_key: str):
    openai.api_key = api_key


def parse_options(response_content: str) -> List[Tuple[str, str]]:
    """
    Assumes response_content is formatted as:
    Option 1:
    "Response 1 in respondent language"
    "Translation of response 1 in English"

    Option 2:
    "Response 2 in respondent language"
    "Translation of response 2 in English"

    ...
    """
    options = response_content.split("Option")
    result = []
    for option in options:
        if len(option.strip()) == 0:
            continue
        # Remove leading and trailing quotes and whitespace
        lines = [line.strip()[1:-1] for line in option.split("\n") if line.strip()]
        result.append((lines[1], lines[2]))

    return result


def extract_message_from_openai_response(
    response: openai.openai_object.OpenAIObject,
) -> str:
    """
    Extract the actual GPT message from an OpenAI response
    """
    return response.choices[0]["message"]["content"]


def gpt_responses(prompt: str, stream: bool) -> openai.openai_object.OpenAIObject:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=stream,
    )
    return response
