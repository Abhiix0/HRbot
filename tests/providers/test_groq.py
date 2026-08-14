from unittest.mock import MagicMock

import groq
import pytest

from hrbot.providers.base import (
    Message,
    ProviderAuthError,
    ProviderConfigError,
    ProviderEmptyResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from hrbot.providers.groq import GroqProvider


def _make_provider(client: MagicMock) -> GroqProvider:
    return GroqProvider(api_key="fake-key", model="llama-3.1-8b-instant", client=client)


def _make_completion(content: str):
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    return completion


def _make_stream_chunks(pieces: list[str]):
    chunks = []
    for piece in pieces:
        chunk = MagicMock()
        chunk.choices = [MagicMock(delta=MagicMock(content=piece))]
        chunks.append(chunk)
    return chunks


class TestConfiguration:
    def test_missing_api_key_raises_config_error(self):
        with pytest.raises(ProviderConfigError):
            GroqProvider(api_key=None)

    def test_injected_client_bypasses_key_requirement(self):
        # Should not raise even with no api_key, since a client is supplied.
        provider = GroqProvider(api_key=None, client=MagicMock())
        assert provider is not None


class TestGenerate:
    def test_successful_generation(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _make_completion("Hi there!")
        provider = _make_provider(client)

        result = provider.generate([Message(role="user", content="Hello")])

        assert result == "Hi there!"
        client.chat.completions.create.assert_called_once()
        _, kwargs = client.chat.completions.create.call_args
        assert kwargs["stream"] is False
        assert kwargs["messages"] == [{"role": "user", "content": "Hello"}]

    def test_empty_response_raises(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _make_completion("")
        provider = _make_provider(client)

        with pytest.raises(ProviderEmptyResponseError):
            provider.generate([Message(role="user", content="Hello")])

    def test_authentication_error_normalized(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = groq.AuthenticationError(
            "bad key", response=MagicMock(), body=None
        )
        provider = _make_provider(client)

        with pytest.raises(ProviderAuthError):
            provider.generate([Message(role="user", content="Hello")])

    def test_rate_limit_error_normalized(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = groq.RateLimitError(
            "slow down", response=MagicMock(), body=None
        )
        provider = _make_provider(client)

        with pytest.raises(ProviderRateLimitError):
            provider.generate([Message(role="user", content="Hello")])

    def test_timeout_error_normalized(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = groq.APITimeoutError(request=MagicMock())
        provider = _make_provider(client)

        with pytest.raises(ProviderTimeoutError):
            provider.generate([Message(role="user", content="Hello")])


class TestStream:
    def test_successful_streaming(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _make_stream_chunks(
            ["Hel", "lo", " there"]
        )
        provider = _make_provider(client)

        result = list(provider.stream([Message(role="user", content="Hi")]))

        assert result == ["Hel", "lo", " there"]
        _, kwargs = client.chat.completions.create.call_args
        assert kwargs["stream"] is True

    def test_empty_stream_raises(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _make_stream_chunks([])
        provider = _make_provider(client)

        with pytest.raises(ProviderEmptyResponseError):
            list(provider.stream([Message(role="user", content="Hi")]))

    def test_stream_provider_failure_normalized(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = groq.RateLimitError(
            "slow down", response=MagicMock(), body=None
        )
        provider = _make_provider(client)

        with pytest.raises(ProviderRateLimitError):
            list(provider.stream([Message(role="user", content="Hi")]))
