import pytest
import requests

from app.translation.deepl import extract_translation_from_deepl_response


@pytest.fixture
def deepl_response():
    response = requests.Response()
    response._content = (
        b'{"translations": [{"detected_source_language": "EN", "text": "Bonjour"}]}'
    )
    return response


def test_extract_translation_from_deepl_response(deepl_response):
    translation = extract_translation_from_deepl_response(deepl_response)
    assert translation == "Bonjour"
