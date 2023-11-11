from enum import Enum
from typing import Dict, List, Tuple

import openai


class OpenAIStreamDFAState(Enum):
    START_TAG = "start_tag"
    END_TAG = "end_tag"
    INSIDE = "inside"
    OUTSIDE = "outside"


class OpenAIReponseOptionStreamDFA:
    """
    Parse the RESPONSE_OPTIONS prompt output. Assumes the output is formatted as:
    <Start>
    "Response 1"
    <End>
    ...
    """

    START_TAG = "<Start>"
    END_TAG = "<End>"

    def __init__(self):
        self.state = OpenAIStreamDFAState.OUTSIDE
        self.response_chars: List[str] = []
        self.response_start_idx = -1
        self.open_angle_bracket_idx: List[int] = []
        self.prev_non_whitespace_char_idx = -1
        # List of (start_idx, end_idx) tuples where start_idx is inclusive
        # and end_idx is exclusive
        self.message_idx: List[Tuple[int, int]] = []

    def is_response_start(self, idx: int) -> bool:
        """Return whether idx is the last character of a start token"""
        start_token_len = len(__class__.START_TAG)
        start_idx = idx - start_token_len + 1
        end_idx = idx + 1
        return "".join(self.response_chars[start_idx:end_idx]) == self.START_TAG

    def is_response_end(self, idx: int) -> bool:
        """Return whether idx is the first character after a start token"""
        end_token_len = len(__class__.END_TAG)
        start_idx = idx - end_token_len + 1
        end_idx = idx + 1
        return "".join(self.response_chars[start_idx:end_idx]) == self.END_TAG

    def process_char(self, char: str) -> Dict[str, str]:
        self.response_chars.append(char)

        if self.state == OpenAIStreamDFAState.OUTSIDE:
            if char == "<":
                self.state = OpenAIStreamDFAState.START_TAG
                self.open_angle_bracket_idx.append(len(self.response_chars) - 1)
                return {}
            elif not char.isalpha():
                return {}
            else:
                raise ValueError(f"Unexpected char {char} in state {self.state}")

        elif self.state == OpenAIStreamDFAState.START_TAG:
            idx = len(self.response_chars) - 1
            if len(self.open_angle_bracket_idx) > 0:
                start_tag_pos = idx - self.open_angle_bracket_idx[-1]
                if char != __class__.START_TAG[start_tag_pos]:
                    raise ValueError(f"Unexpected char {char} in state {self.state}")
                else:
                    if char == ">":
                        self.open_angle_bracket_idx.pop()
                    return {}
            elif char.isspace():
                return {}
            elif char == '"':
                assert len(self.open_angle_bracket_idx) == 0
                self.state = OpenAIStreamDFAState.INSIDE
                self.response_start_idx = idx + 1
                return {}

        elif self.state == OpenAIStreamDFAState.END_TAG:
            idx = len(self.response_chars) - 1
            end_tag_pos = idx - self.open_angle_bracket_idx[-1]
            if char != __class__.END_TAG[end_tag_pos]:
                raise ValueError(f"Unexpected char {char} in state {self.state}")

            if char == ">":
                self.open_angle_bracket_idx.pop()
            if end_tag_pos == len(__class__.END_TAG) - 1:
                self.state = OpenAIStreamDFAState.OUTSIDE
            return {}

        elif self.state == OpenAIStreamDFAState.INSIDE:
            if char == '"':
                self.prev_non_whitespace_char_idx = len(self.response_chars) - 1
                return {}
            elif self.response_chars[self.prev_non_whitespace_char_idx] == '"':
                if char.isspace():
                    return {}
                # Assumes every angle bracket following a quote is the end tag
                elif char == "<":
                    self.state = OpenAIStreamDFAState.END_TAG
                    self.message_idx.append(
                        (self.response_start_idx, self.prev_non_whitespace_char_idx)
                    )
                    self.prev_non_whitespace_char_idx = -1
                    self.response_start_idx = -1
                    self.open_angle_bracket_idx.append(len(self.response_chars) - 1)
                    return {"event": "end"}
                else:
                    # Include everything from the previous quote in the message to the end,
                    # since it was previously ommitted
                    ret = {
                        "data": self.response_chars[
                            self.prev_non_whitespace_char_idx :
                        ],
                        "event": "message",
                    }
                    self.prev_non_whitespace_char_idx = len(self.response_chars) - 1
                    return ret
            else:
                return {"data": char, "event": "message"}

    def combine_return_events(
        self, return_events: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        combined: List[Dict[str, str]] = []
        curr_message: List[str] = []
        for event in return_events:
            if "event" not in event:
                continue
            elif event["event"] == "message":
                curr_message.append(event["data"])
            elif event["event"] == "end":
                combined.append({"event": "message", "data": "".join(curr_message)})
                curr_message = []
                combined.append(event)

        if len(curr_message) > 0:
            combined.append({"event": "message", "data": "".join(curr_message)})

        return combined

    def process_chunk(self, event: Dict[str, str]) -> Dict[str, str]:
        if extract_finish_reason_from_openai_response_chunk(event) == "stop":
            return {"event": "stop"}

        message = extract_message_from_openai_response_chunk(event)
        return_events: List[Dict[str, str]] = []
        for char in message:
            return_events.append(self.process_char(char))

        return self.combine_return_events(return_events)


def parse_streamed_options(text: str) -> List[str]:
    # Split the text by the <Start> and <End> tags
    parts = text.split("<End>")

    options = []
    for part in parts:
        # Check if <Start> is in the part
        if "<Start>" in part:
            # Extract the response between <Start> and <End>
            option = part.split("<Start>")[1].strip()
            # Remove quotes and add to the list
            option = option.strip()
            option = option.strip('"')
            option = option.strip()
            options.append(option)

    return options


def parse_options(response_content: str) -> List[str]:
    """
    Assumes response_content is formatted as:
    Option 1:
    "Response 1 in respondent language"

    Option 2:
    "Response 2 in respondent language"

    ...
    """
    options = response_content.split("Option")
    result = []
    for option in options:
        if len(option.strip()) == 0:
            continue
        # Remove leading and trailing quotes and whitespace
        lines = [line.strip()[1:-1] for line in option.split("\n") if line.strip()]
        result.append(lines[1])

    return result


def parse_options_with_translations(response_content: str) -> List[Tuple[str, str]]:
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
    response: openai.types.chat.chat_completion.ChatCompletion,
) -> str:
    """
    Extract the actual GPT message from an OpenAI response
    """
    return response.choices[0].message.content


def extract_message_from_openai_response_chunk(
    chunk: openai.types.chat.chat_completion_chunk.ChatCompletionChunk,
) -> str:
    """
    Extract the actual GPT message from an OpenAI response chunk
    stream response
    """
    return chunk.choices[0].delta.content


def extract_finish_reason_from_openai_response_chunk(
    chunk: openai.types.chat.chat_completion_chunk.ChatCompletionChunk,
) -> str:
    """
    Extract the stop reason from an OpenAI response chunk
    stream response
    """
    return chunk.choices[0].finish_reason


def gpt_responses(
    openai_client: openai.OpenAI, prompt: str, stream: bool
) -> openai.Stream | openai.types.chat.chat_completion.ChatCompletion:
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=stream,
    )
    return response
