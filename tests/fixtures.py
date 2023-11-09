import pytest

from app.constants.language import Language
from app.models import Conversation, ConversationParticipant, Message


@pytest.fixture
def message():
    message = Message(
        id="2f76f523-3989-44b2-b335-011f7dbcdfc7",
        sender=ConversationParticipant.USER,
        content="Hello",
        translation="Bonjour",
        tts_uri="bonjour.mp3",
        tts_task_id="asdf",
    )
    return message


@pytest.fixture
def conversation(message):
    conversation = Conversation(
        id="614d7b95-1ce8-49e5-abc2-4357f91a6ae1",
        intro_message="This is a translation app.",
        history=[message],
        user_lang=Language.ENGLISH,
        resp_lang=Language.FRENCH,
    )
    return conversation


@pytest.fixture
def two_message_mandarin_french_conversation():
    message1 = Message(
        sender=ConversationParticipant.USER,
        content="Bonjour. Je cherche le vol pour les pays-bas.",
        translation="您好。我正在寻找飞往荷兰的航班。",
    )
    message2 = Message(
        sender=ConversationParticipant.RESPONDENT,
        content="你要去哪个城市",
        translation="Quelle est votre ville de destination ?",
    )

    conversation = Conversation(
        id="614d7b95-1ce8-49e5-abc2-4357f91a6ae1",
        intro_message="This is a translation app.",
        history=[message1, message2],
        user_lang=Language.FRENCH,
        resp_lang=Language.MANDARIN,
    )
    return conversation
