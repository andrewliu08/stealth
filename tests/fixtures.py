import pytest

from app.constants.language import Language
from app.models import Conversation, ConversationParticipant, Message


@pytest.fixture
def message():
    message = Message(
        sender=ConversationParticipant.USER,
        content="Hello",
        translation="Bonjour",
        tts_uri="bonjour.mp3",
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
