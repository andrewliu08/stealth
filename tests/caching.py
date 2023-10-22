import pytest

from app.caching import new_conversation, get_conversation
from tests.test_fixtures import conversation, message
from tests.test_utils import conversations_equal


class MockRedisClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.cache = {}

    def set(self, key: str, value: str):
        self.cache[key] = value

    def get(self, key: str) -> str:
        return self.cache[key]


@pytest.fixture
def redis_client():
    return MockRedisClient(host="localhost", port=6379)


def test_new_conversation(conversation):
    redis_client = MockRedisClient(host="localhost", port=6379)
    new_conversation(redis_client, conversation)

    assert conversation.id in redis_client.cache
    assert redis_client.cache[conversation.id] == conversation.to_cacheable_str()


def test_get_conversation(conversation):
    redis_client = MockRedisClient(host="localhost", port=6379)
    new_conversation(redis_client, conversation)

    conversation2 = get_conversation(redis_client, conversation.id)
    assert conversations_equal(conversation, conversation2)
