from unittest.mock import patch

from src.chatbot.chat import get_response


def test_get_response_returns_string():
    with patch("src.chatbot.chat.get_llm_response", return_value="Hello!"):
        with patch("src.chatbot.chat.get_system_prompt", return_value="You are helpful."):
            result = get_response("Hi")
    assert isinstance(result, str)
    assert result == "Hello!"


def test_generate_response_mock():
    with patch("src.chatbot.chat.get_llm_response", return_value="Mocked response"):
        with patch("src.chatbot.chat.get_system_prompt", return_value="prompt"):
            result = get_response("test input")
    assert result == "Mocked response"


def test_get_response_non_empty():
    with patch("src.chatbot.chat.get_llm_response", return_value="Sure!"):
        with patch("src.chatbot.chat.get_system_prompt", return_value="prompt"):
            result = get_response("Tell me something")
    assert result != ""
