from app.constants.language import Language
from app.generative.prompts import get_conversation_turns, get_prompt
from app.models import ConversationParticipant, Message
from tests.fixtures import (
    conversation,
    message,
    two_message_mandarin_french_conversation,
)


def test_get_conversation_turns(conversation):
    resp_message = Message(
        sender=ConversationParticipant.RESPONDENT,
        content="Salut! Comment ca va?",
        translation="Hi! How are you?",
    )
    conversation.history.append(resp_message)

    conversation_turns = get_conversation_turns(conversation)
    assert conversation_turns == [
        "You:\nBonjour",
        "Other:\nSalut! Comment ca va?",
    ]


def test_get_conversation_turns_remove_intro_message(conversation):
    intro_message = "J'utilise une application de traduction. Veuillez parler dans le téléphone lorsque vous répondez."
    conversation.history[0].translation += f"\n\n {intro_message}"

    conversation_turns = get_conversation_turns(conversation)
    assert conversation_turns == ["You:\nBonjour"]


def test_get_prompt(conversation):
    resp_message = Message(
        sender=ConversationParticipant.RESPONDENT,
        content="Salut! Comment ca va?",
        translation="Hi! How are you?",
    )
    conversation.history.append(resp_message)

    prompt = get_prompt(conversation, num_response_options=3)
    expected_prompt = '''You are a fluent french speaker having a conversation in french. The conversation so far is in triple quotes:
"""
You:
Bonjour

Other:
Salut! Comment ca va?
"""
Provide 3 options for what you might say to the other person. For each option, provide an english translation of what you said. Follow the format in the triple quotes:
"""
Option 1:
"Response 1 in french"
"Translation of response 1 in english"

Option 2:
"Response 2 in french"
"Translation of response 2 in english"

Option 3:
"Response 3 in french"
"Translation of response 3 in english"
"""
'''
    assert prompt == expected_prompt


def test_get_prompt1(two_message_mandarin_french_conversation):
    prompt = get_prompt(
        two_message_mandarin_french_conversation, num_response_options=3
    )
    expected_prompt = '''You are a fluent mandarin speaker having a conversation in mandarin. The conversation so far is in triple quotes:
"""
You:
您好。我正在寻找飞往荷兰的航班。

Other:
你要去哪个城市
"""
Provide 3 options for what you might say to the other person. For each option, provide an french translation of what you said. Follow the format in the triple quotes:
"""
Option 1:
"Response 1 in mandarin"
"Translation of response 1 in french"

Option 2:
"Response 2 in mandarin"
"Translation of response 2 in french"

Option 3:
"Response 3 in mandarin"
"Translation of response 3 in french"
"""
'''
    assert prompt == expected_prompt
