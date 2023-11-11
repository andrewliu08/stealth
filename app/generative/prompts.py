from typing import List

from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.gpt_prompts import (
    RESPONSE_OPTIONS_PROMPT,
    RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS,
    RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS_AND_GOAL,
)
from app.models import Conversation, ConversationParticipant


def get_conversation_turns(
    conversation: Conversation, use_user_lang: bool
) -> List[str]:
    """
    Get a list of strings where each element is a turn in the conversation.
    The conversation will be in the user's language if use_user_lang is True,
    otherwise in the respondent's language
    """
    history = []
    for i, message in enumerate(conversation.history):
        if message.sender == ConversationParticipant.USER:
            content = message.content if use_user_lang else message.translation
            s = "Person 1:\n" + content
            # Remove intro message when prompting
            if i == 0:
                for intro_message in INTRO_MESSAGE_TRANSLATIONS.values():
                    s = s.replace(intro_message, "")
        else:
            content = message.content if not use_user_lang else message.translation
            s = "Person 2:\n" + content
        history.append(s.strip())
    return history


def get_prompt(conversation: Conversation, num_response_options: int) -> str:
    """Create the prompt used to get potential responses from GPT"""
    history = get_conversation_turns(conversation, use_user_lang=True)
    history_str = "\n\n".join(history)
    prompt = RESPONSE_OPTIONS_PROMPT.format(
        conversation.user_lang.value,
        history_str,
        num_response_options,
    )
    return prompt


def get_prompt_with_translations(
    conversation: Conversation,
    num_response_options: int,
) -> str:
    """Create the prompt used to get potential responses from GPT"""
    history = get_conversation_turns(conversation, use_user_lang=False)
    history_str = "\n\n".join(history)
    prompt = RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS.format(
        conversation.resp_lang.value,
        conversation.user_lang.value,
        history_str,
        num_response_options,
    )
    return prompt


def get_prompt_with_translations_and_goal(
    goal: str,
    conversation: Conversation,
    num_response_options: int,
) -> str:
    """Create the prompt used to get potential responses from GPT"""
    history = get_conversation_turns(conversation, use_user_lang=False)
    history_str = "\n\n".join(history)
    prompt = RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS_AND_GOAL.format(
        conversation.resp_lang.value, goal, history_str, num_response_options
    )
    return prompt
