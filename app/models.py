from enum import Enum
from typing import Any, Dict, List, Optional

from app.constants.language import Language


class ConversationParticipant(Enum):
    USER = "user"
    RESPONDENT = "respondent"


class Message:
    def __init__(
        self,
        id: str = "",
        sender: Optional[ConversationParticipant] = None,
        content: str = "",
        translation: str = "",
        tts_uri: str = "",
        tts_task_id: Optional[str] = None,
    ):
        self.id = id
        self.sender = sender
        self.content = content
        self.translation = translation
        self.tts_uri = tts_uri
        self.tts_task_id = tts_task_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender.value,
            "content": self.content,
            "translation": self.translation,
            "tts_uri": self.tts_uri,
            "tts_task_id": self.tts_task_id,
        }

    def to_cacheable_str(self) -> str:
        d = {
            "id": self.id,
            "sender": self.sender.value,
            "content": self.content,
            "translation": self.translation,
            "tts_uri": self.tts_uri,
            "tts_task_id": self.tts_task_id,
        }
        return str(d)

    def from_cacheable_str(self, s: str):
        d = eval(s)
        self.id = d["id"]
        self.sender = ConversationParticipant(d["sender"])
        self.content = d["content"]
        self.translation = d["translation"]
        self.tts_uri = d["tts_uri"] if "tts_uri" in d else ""
        self.tts_task_id = d["tts_task_id"] if "tts_task_id" in d else None

    def __repr__(self) -> str:
        return "Message(id={}, sender={}, content={}, translation={}, tts_uri={}, tts_task_id={})".format(
            self.id,
            self.sender,
            self.content,
            self.translation,
            self.tts_uri,
            self.tts_task_id,
        )


class Conversation:
    def __init__(
        self,
        id: str = "",
        intro_message: Optional[Message] = None,
        history: List[Message] = [],
        user_lang: Optional[Language] = None,
        resp_lang: Optional[Language] = None,
    ):
        self.id = id
        self.intro_message = intro_message
        self.history = history
        self.user_lang = user_lang
        self.resp_lang = resp_lang

    def new_message(self, message: Message):
        self.history.append(message)

    def get_message(self, message_id: Message) -> Optional[Message]:
        for message in self.history:
            if message.id == message_id:
                return message

        return None

    def delete_message(self, message_id: str) -> bool:
        """Delete message with id `message_id` and all subsequent messages"""
        for i, message in enumerate(self.history):
            if message.id == message_id:
                self.history = self.history[:i]
                return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "intro_message": self.intro_message,
            "history": [message.to_dict() for message in self.history],
            "user_lang": self.user_lang.value,
            "resp_lang": self.resp_lang.value,
        }

    def to_cacheable_str(self) -> str:
        d = {
            "id": self.id,
            "intro_message": self.intro_message,
            "history": [message.to_cacheable_str() for message in self.history],
            "user_lang": self.user_lang.value,
            "resp_lang": self.resp_lang.value,
        }
        return str(d)

    def from_cacheable_str(self, s: str):
        d = eval(s)
        self.id = d["id"]
        self.intro_message = d["intro_message"]

        self.history = []
        for message_dict in d["history"]:
            message = Message()
            message.from_cacheable_str(message_dict)
            self.history.append(message)

        self.user_lang = Language(d["user_lang"])
        self.resp_lang = Language(d["resp_lang"])

    def __repr__(self) -> str:
        return "ConversationHistory(id={}, intro_message={}, history={}, user_lang={}, resp_lang={})".format(
            self.id, self.intro_message, self.history, self.user_lang, self.resp_lang
        )
