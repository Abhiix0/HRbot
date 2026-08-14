from unittest.mock import MagicMock, patch

from hrbot.core import service


def _patch_common(response_text: str = "Hello!"):
    fake_provider = MagicMock()
    fake_provider.generate.return_value = response_text
    return (
        patch.object(service, "get_provider", return_value=fake_provider),
        patch.object(service, "get_system_prompt", return_value="You are helpful."),
        patch.object(service.retriever, "search", return_value=""),
    )


def test_get_response_returns_string():
    patches = _patch_common("Hello!")
    with patches[0], patches[1], patches[2]:
        result = service.get_response("Hi")
    assert isinstance(result, str)
    assert result == "Hello!"


def test_generate_response_mock():
    patches = _patch_common("Mocked response")
    with patches[0], patches[1], patches[2]:
        result = service.get_response("test input")
    assert result == "Mocked response"


def test_get_response_non_empty():
    patches = _patch_common("Sure!")
    with patches[0], patches[1], patches[2]:
        result = service.get_response("Tell me something")
    assert result != ""


def test_get_response_updates_history():
    patches = _patch_common("Answer")
    with patches[0], patches[1], patches[2]:
        service.get_response("What are the hours?")
    history = service.get_history()
    assert history[-2].role == "user"
    assert history[-1].role == "assistant"
    assert history[-1].content == "Answer"
