"""Groq implementation of LLMProvider.

This is the only file in the application that is allowed to import the
`groq` SDK or know that "Groq" exists. Everything it raises is translated
into the normalized errors defined in `hrbot.providers.base`.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import groq

from hrbot.providers.base import (
    LLMProvider,
    Message,
    ProviderAPIError,
    ProviderAuthError,
    ProviderConfigError,
    ProviderEmptyResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama-3.1-8b-instant"


class GroqProvider(LLMProvider):
    """LLMProvider backed by Groq / Llama 3.1 8B Instant."""

    def __init__(
        self,
        api_key: str | None,
        model: str = DEFAULT_MODEL,
        client: groq.Groq | None = None,
    ) -> None:
        if not api_key and client is None:
            raise ProviderConfigError(
                "GROQ_API_KEY is not set. Configure it in your .env file."
            )
        self._model = model
        # `client` can be injected directly in tests to avoid touching the
        # network or requiring a real API key.
        self._client = client or groq.Groq(api_key=api_key)

    def generate(self, messages: list[Message]) -> str:
        payload = self._to_groq_messages(messages)
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=payload,
                stream=False,
            )
        except Exception as exc:
            raise self._normalize(exc) from exc

        content = completion.choices[0].message.content if completion.choices else None
        if not content or not content.strip():
            raise ProviderEmptyResponseError("Groq returned an empty response.")
        return content

    def stream(self, messages: list[Message]) -> Iterator[str]:
        payload = self._to_groq_messages(messages)
        try:
            chunks = self._client.chat.completions.create(
                model=self._model,
                messages=payload,
                stream=True,
            )
            received_any = False
            for chunk in chunks:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    received_any = True
                    yield delta
        except Exception as exc:
            raise self._normalize(exc) from exc

        if not received_any:
            raise ProviderEmptyResponseError("Groq returned an empty response.")

    @staticmethod
    def _to_groq_messages(messages: list[Message]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    @staticmethod
    def _normalize(exc: Exception) -> Exception:
        """Translate a groq SDK exception into a normalized ProviderError."""
        if isinstance(exc, groq.AuthenticationError):
            return ProviderAuthError("Groq rejected the API key.")
        if isinstance(exc, groq.RateLimitError):
            return ProviderRateLimitError("Groq rate limit exceeded.")
        if isinstance(exc, groq.APITimeoutError):
            return ProviderTimeoutError("Groq request timed out.")
        if isinstance(exc, groq.APIConnectionError):
            return ProviderTimeoutError("Could not connect to Groq.")
        if isinstance(exc, groq.APIStatusError):
            return ProviderAPIError(f"Groq API error: {exc}")
        logger.exception("Unexpected error calling Groq")
        return ProviderAPIError(f"Unexpected Groq failure: {exc}")
