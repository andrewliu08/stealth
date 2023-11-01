from typing import List

from app.constants.intro_messages import INTRO_MESSAGE_TRANSLATIONS
from app.constants.gpt_prompts import (
    RESPONSE_OPTIONS_PROMPT,
    RESPONSE_OPTIONS_WITH_GOAL_PROMPT,
)
from app.models import Conversation, ConversationParticipant


def get_conversation_turns(conversation: Conversation) -> List[str]:
    """
    Get a list of strings where each element is a turn in the conversation
    in the respondent's language
    """
    history = []
    for i, message in enumerate(conversation.history):
        if message.sender == ConversationParticipant.USER:
            s = "You:\n" + message.translation
            # Remove intro message when prompting
            if i == 0:
                for intro_message in INTRO_MESSAGE_TRANSLATIONS.values():
                    s = s.replace(intro_message, "")
        else:
            s = "Other:\n" + message.content
        history.append(s.strip())
    return history


def get_prompt_with_goal(
    goal: str,
    conversation: Conversation,
    num_response_options: int,
) -> str:
    """Create the prompt used to get potential responses from GPT"""
    history = get_conversation_turns(conversation)
    history_str = "\n\n".join(history)
    prompt = RESPONSE_OPTIONS_WITH_GOAL_PROMPT.format(
        conversation.resp_lang.value, goal, history_str, num_response_options
    )
    return prompt


def get_prompt(
    conversation: Conversation,
    num_response_options: int,
) -> str:
    """Create the prompt used to get potential responses from GPT"""
    history = get_conversation_turns(conversation)
    history_str = "\n\n".join(history)
    prompt = RESPONSE_OPTIONS_PROMPT.format(
        conversation.resp_lang.value,
        conversation.user_lang.value,
        history_str,
        num_response_options,
    )
    return prompt
