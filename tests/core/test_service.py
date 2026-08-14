from unittest.mock import patch

from hrbot.core.service import get_response
from hrbot.knowledge.schema import RetrievalResult


def test_get_response_returns_string():
    mock_result = RetrievalResult(
        query="Hi",
        matches=[],
        top_score=0.0,
        confidence="none",
    )
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Hello!"),
        patch("hrbot.core.service.get_system_prompt", return_value="You are helpful."),
        patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),
    ):
        result = get_response("Hi")
    assert isinstance(result, str)
    assert result == "Hello!"


def test_generate_response_mock():
    mock_result = RetrievalResult(
        query="test input",
        matches=[],
        top_score=0.0,
        confidence="none",
    )
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Mocked response"),
        patch("hrbot.core.service.get_system_prompt", return_value="prompt"),
        patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),
    ):
        result = get_response("test input")
    assert result == "Mocked response"


def test_get_response_non_empty():
    mock_result = RetrievalResult(
        query="Tell me something",
        matches=[],
        top_score=0.0,
        confidence="none",
    )
    with (
        patch("hrbot.core.service.get_llm_response", return_value="Sure!"),
        patch("hrbot.core.service.get_system_prompt", return_value="prompt"),
        patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),
    ):
        result = get_response("Tell me something")
    assert result != ""
