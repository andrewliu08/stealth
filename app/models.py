from enum import Enum
from typing import Any, Dict, List, Optional

from app.constants.language import Language


class ConversationParticipant(Enum):
    USER = "user"
    RESPONDENT = "respondent"


class Message:
    def __init__(
        self,
        sender: Optional[ConversationParticipant] = None,
        content: str = "",
        translation: str = "",
        tts_uri: str = "",
    ):
        self.sender = sender
        self.content = content
        self.translation = translation
        self.tts_uri = tts_uri

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender.value,
            "content": self.content,
            "translation": self.translation,
            "tts_uri": self.tts_uri,
        }

    def to_cacheable_str(self) -> str:
        d = {
            "sender": self.sender.value,
            "content": self.content,
            "translation": self.translation,
            "tts_uri": self.tts_uri,
        }
        return str(d)

    def from_cacheable_str(self, s: str):
        d = eval(s)
        self.sender = ConversationParticipant(d["sender"])
        self.content = d["content"]
        self.translation = d["translation"]
        self.tts_uri = d["tts_uri"] if "tts_uri" in d else ""

    def __repr__(self) -> str:
        return "Message(sender={}, content={}, translation={}, tts_uri={})".format(
            self.sender,
            self.content,
            self.translation,
            self.tts_uri,
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "intro_message": self.intro_message,
            "history": [message.to_dict() for message in self.history],
            "user_lang": self.user_lang.value.capitalize(),
            "resp_lang": self.resp_lang.value.capitalize(),
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
