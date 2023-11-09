import uuid
from typing import Optional

import redis

from app.models import Conversation


class MockRedisClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.cache = {}

    def set(self, key: str, value: str):
        self.cache[key] = value

    def get(self, key: str) -> Optional[str]:
        return self.cache.get(key)

    def keys(self):
        return self.cache.keys()


def create_redis_client(host, port):
    # return redis.Redis(host=host, port=port, decode_responses=True)
    return MockRedisClient(host=host, port=port)


def create_id():
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


def get_all_keys(redis_client: redis.Redis):
    # for key in redis_client.scan_iter():
    #     print(key)
    return redis_client.keys()
