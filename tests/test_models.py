from app.models import Conversation, ConversationParticipant, Message
from tests.fixtures import conversation, message
from tests.utils import conversations_equal, messages_equal


def test_message_to_dict(message):
    message_dict = message.to_dict()
    assert isinstance(message_dict, dict)

    assert message_dict["sender"] == "user"
    assert message_dict["content"] == "Hello"
    assert message_dict["translation"] == "Bonjour"
    assert message_dict["tts_uri"] == "bonjour.mp3"


def test_message_cacheable_str(message):
    cacheable_repr = message.to_cacheable_str()
    assert isinstance(cacheable_repr, str)

    message2 = Message()
    message2.from_cacheable_str(cacheable_repr)

    assert messages_equal(message, message2)


def test_conversation_to_dict(conversation):
    conversation_dict = conversation.to_dict()
    assert isinstance(conversation_dict, dict)

    assert conversation_dict["id"] == "614d7b95-1ce8-49e5-abc2-4357f91a6ae1"
    assert len(conversation_dict["history"]) == 1

    assert conversation_dict["history"][0]["content"] == "Hello"
    assert conversation_dict["history"][0]["translation"] == "Bonjour"
    assert conversation_dict["history"][0]["tts_uri"] == "bonjour.mp3"

    assert conversation_dict["user_lang"] == "english"
    assert conversation_dict["resp_lang"] == "french"


def test_conversation_cacheable_str(conversation):
    cacheable_repr = conversation.to_cacheable_str()
    assert isinstance(cacheable_repr, str)

    conversation2 = Conversation()
    conversation2.from_cacheable_str(cacheable_repr)

    assert conversations_equal(conversation, conversation2)


def test_conversation_new_message(conversation):
    new_message = Message(
        sender=ConversationParticipant.RESPONDENT,
        content="Au revoir",
        translation="Bye",
        tts_uri="au_revoir.mp3",
    )
    conversation.new_message(new_message)
    assert len(conversation.history) == 2

    assert conversation.history[0].sender == ConversationParticipant.USER
    assert conversation.history[0].content == "Hello"
    assert conversation.history[0].translation == "Bonjour"
    assert conversation.history[0].tts_uri == "bonjour.mp3"

    assert conversation.history[1].sender == ConversationParticipant.RESPONDENT
    assert conversation.history[1].content == "Au revoir"
    assert conversation.history[1].translation == "Bye"
    assert conversation.history[1].tts_uri == "au_revoir.mp3"
