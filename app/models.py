from typing import Any, Dict, List, Optional

from app.language import Language


class Message:
    def __init__(
        self,
        content: str = "",
        translation: str = "",
        content_tts_uri: str = "",
        translation_tts_uri: str = "",
    ):
        self.content = content
        self.translation = translation
        self.content_tts_uri = content_tts_uri
        self.translation_tts_uri = translation_tts_uri

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "translation": self.translation,
            "content_tts_uri": self.content_tts_uri,
            "translation_tts_uri": self.translation_tts_uri,
        }

    def to_cacheable_str(self) -> str:
        d = {
            "content": self.content,
            "translation": self.translation,
            "content_tts_uri": self.content_tts_uri,
            "translation_tts_uri": self.translation_tts_uri,
        }
        return str(d)

    def from_cacheable_str(self, s: str):
        d = eval(s)
        self.content = d["content"]
        self.translation = d["translation"]
        self.content_tts_uri = d["content_tts_uri"] if "content_tts_uri" in d else ""
        self.translation_tts_uri = (
            d["translation_tts_uri"] if "translation_tts_uri" in d else ""
        )

    def __repr__(self) -> str:
        return "Message(content={}, translation={}, content_tts_uri={}, translation_tts_uri={})".format(
            self.content,
            self.translation,
            self.content_tts_uri,
            self.translation_tts_uri,
        )


class Conversation:
    def __init__(
        self,
        id: str = "",
        history: List[Message] = [],
        user_lang: Optional[Language] = None,
        resp_lang: Optional[Language] = None,
    ):
        self.id = id
        self.history = history
        self.user_lang = user_lang
        self.resp_lang = resp_lang

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "history": [message.to_dict() for message in self.history],
            "user_lang": self.user_lang.value,
            "resp_lang": self.resp_lang.value,
        }

    def to_cacheable_str(self) -> str:
        d = {
            "id": self.id,
            "history": [message.to_cacheable_str() for message in self.history],
            "user_lang": self.user_lang.value,
            "resp_lang": self.resp_lang.value,
        }
        return str(d)

    def from_cacheable_str(self, s: str):
        d = eval(s)
        self.id = d["id"]

        self.history = []
        for message_dict in d["history"]:
            message = Message()
            message.from_cacheable_str(message_dict)
            self.history.append(message)

        self.user_lang = Language(d["user_lang"])
        self.resp_lang = Language(d["resp_lang"])

    def __repr__(self) -> str:
        return (
            "ConversationHistory(id={}, history={}, user_lang={}, resp_lang={})".format(
                self.id, self.history, self.user_lang, self.resp_lang
            )
        )
