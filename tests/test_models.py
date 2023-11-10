from app.models import Conversation, ConversationParticipant, Message
from tests.fixtures import conversation, message
from tests.utils import conversations_equal, messages_equal


def test_message_to_dict(message):
    message_dict = message.to_dict()
    assert isinstance(message_dict, dict)

    assert message_dict["id"] == "2f76f523-3989-44b2-b335-011f7dbcdfc7"
    assert message_dict["sender"] == "user"
    assert message_dict["content"] == "Hello"
    assert message_dict["translation"] == "Bonjour"
    assert message_dict["tts_uri"] == "bonjour.mp3"
    assert message_dict["tts_task_id"] == "asdf"


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

    assert (
        conversation_dict["history"][0]["id"] == "2f76f523-3989-44b2-b335-011f7dbcdfc7"
    )
    assert conversation_dict["history"][0]["sender"] == "user"
    assert conversation_dict["history"][0]["content"] == "Hello"
    assert conversation_dict["history"][0]["translation"] == "Bonjour"
    assert conversation_dict["history"][0]["tts_uri"] == "bonjour.mp3"
    assert conversation_dict["history"][0]["tts_task_id"] == "asdf"

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
        tts_task_id="a",
    )
    conversation.new_message(new_message)
    assert len(conversation.history) == 2

    assert conversation.history[0].sender == ConversationParticipant.USER
    assert conversation.history[0].content == "Hello"
    assert conversation.history[0].translation == "Bonjour"
    assert conversation.history[0].tts_uri == "bonjour.mp3"
    assert conversation.history[0].tts_task_id == "asdf"

    assert conversation.history[1].sender == ConversationParticipant.RESPONDENT
    assert conversation.history[1].content == "Au revoir"
    assert conversation.history[1].translation == "Bye"
    assert conversation.history[1].tts_uri == "au_revoir.mp3"
    assert conversation.history[1].tts_task_id == "a"


def test_conversation_get_message_exists(conversation):
    message = conversation.get_message("2f76f523-3989-44b2-b335-011f7dbcdfc7")
    assert message is not None
    assert messages_equal(
        message,
        Message(
            id="2f76f523-3989-44b2-b335-011f7dbcdfc7",
            sender=ConversationParticipant.USER,
            content="Hello",
            translation="Bonjour",
            tts_uri="bonjour.mp3",
            tts_task_id="asdf",
        ),
    )


def test_conversation_get_message_does_not_exist(conversation):
    message = conversation.get_message("a")
    assert message is None


def test_conversation_delete_message_success(conversation):
    successfully_deleted = conversation.delete_message(
        "2f76f523-3989-44b2-b335-011f7dbcdfc7"
    )
    assert len(conversation.history) == 0
    assert successfully_deleted


def test_conversation_delete_message_failure(conversation):
    successfully_deleted = conversation.delete_message("a")
    assert len(conversation.history) == 1
    assert not successfully_deleted
