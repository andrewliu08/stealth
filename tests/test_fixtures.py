import pytest

from app.language import Language
from app.models import Conversation, Message


@pytest.fixture
def message():
    message = Message(
        content="Hello",
        translation="Bonjour",
        content_tts_uri="hello.mp3",
        translation_tts_uri="bonjour.mp3",
    )
    return message


@pytest.fixture
def conversation(message):
    conversation = Conversation(
        id="614d7b95-1ce8-49e5-abc2-4357f91a6ae1",
        history=[message],
        user_lang=Language.ENGLISH,
        resp_lang=Language.FRENCH,
    )
    return conversation
