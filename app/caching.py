import uuid
from typing import Optional

import redis

from app.models import Conversation


def create_redis_client(host, port):
    return redis.Redis(host=host, port=port, decode_responses=True)


def create_conversation_id():
    return str(uuid.uuid4())


def save_conversation(redis_client: redis.Redis, conversation: Conversation):
    redis_client.set(conversation.id, conversation.to_cacheable_str())


def get_conversation(
    redis_client: redis.Redis, conversation_id: str
) -> Optional[Conversation]:
    cacheable_repr = redis_client.get(conversation_id)
    if cacheable_repr is None:
        return None

    conversation = Conversation()
    conversation.from_cacheable_str(cacheable_repr)
    return conversation
