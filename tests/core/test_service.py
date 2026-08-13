from unittest.mock import patch

from hrbot.core.service import get_response


def test_get_response_returns_string():
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Hello!"),
        patch("hrbot.core.service.get_system_prompt", return_value="You are helpful."),
        patch("hrbot.core.service.retriever.search", return_value=""),
    ):
        result = get_response("Hi")
    assert isinstance(result, str)
    assert result == "Hello!"


def test_generate_response_mock():
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Mocked response"),
        patch("hrbot.core.service.get_system_prompt", return_value="prompt"),
        patch("hrbot.core.service.retriever.search", return_value=""),
    ):
        result = get_response("test input")
    assert result == "Mocked response"


def test_get_response_non_empty():
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Sure!"),
        patch("hrbot.core.service.get_system_prompt", return_value="prompt"),
        patch("hrbot.core.service.retriever.search", return_value=""),
    ):
        result = get_response("Tell me something")
    assert result != ""
