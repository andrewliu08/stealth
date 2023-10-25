from typing import Optional

import pytest

from app.caching import get_conversation, save_conversation
from tests.fixtures import conversation, message
from tests.utils import conversations_equal


class MockRedisClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.cache = {}

    def set(self, key: str, value: str):
        self.cache[key] = value

    def get(self, key: str) -> Optional[str]:
        return self.cache.get(key)


@pytest.fixture
def redis_client():
    return MockRedisClient(host="localhost", port=6379)


def test_save_conversation(conversation):
    redis_client = MockRedisClient(host="localhost", port=6379)
    save_conversation(redis_client, conversation)

    assert conversation.id in redis_client.cache
    assert redis_client.cache[conversation.id] == conversation.to_cacheable_str()


def test_get_conversation(conversation):
    redis_client = MockRedisClient(host="localhost", port=6379)
    save_conversation(redis_client, conversation)

    conversation2 = get_conversation(redis_client, conversation.id)
    assert conversations_equal(conversation, conversation2)


def test_get_non_existent_conversation(conversation):
    redis_client = MockRedisClient(host="localhost", port=6379)
    conversation = get_conversation(redis_client, "asdf")
    assert conversation is None


def test_overwrite_conversation(conversation, message):
    redis_client = MockRedisClient(host="localhost", port=6379)
    save_conversation(redis_client, conversation)

    conversation2 = get_conversation(redis_client, conversation.id)
    assert conversations_equal(conversation, conversation2)

    conversation.new_message(message)
    save_conversation(redis_client, conversation)

    conversation3 = get_conversation(redis_client, conversation.id)
    assert conversations_equal(conversation, conversation3)
