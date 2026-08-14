"""LLM provider contract.

This module defines the boundary between the application and whatever
LLM backend is actually in use. Nothing outside `hrbot.providers` should
import a provider-specific SDK (e.g. `groq`) or handle provider-specific
exceptions. Everything downstream talks to `LLMProvider` and the plain
`Message` dataclass defined here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Message:
    """A single turn in a conversation, provider-agnostic."""

    role: str  # "system" | "user" | "assistant"
    content: str


# --------------------------------------------------------------------------
# Normalized provider errors.
#
# Every concrete provider must translate its own SDK's exceptions into one
# of these. The rest of the application only ever needs to catch
# `ProviderError` (or a specific subclass if it wants to react differently).
# --------------------------------------------------------------------------


class ProviderError(Exception):
    """Base class for all provider-level failures."""


class ProviderConfigError(ProviderError):
    """Provider could not be constructed (e.g. missing API key)."""


class ProviderTimeoutError(ProviderError):
    """The request to the provider timed out."""


class ProviderAuthError(ProviderError):
    """The provider rejected our credentials."""


class ProviderRateLimitError(ProviderError):
    """The provider is rate-limiting us."""


class ProviderAPIError(ProviderError):
    """A generic/unexpected provider-side failure."""


class ProviderEmptyResponseError(ProviderError):
    """The provider returned no usable content."""


class LLMProvider(ABC):
    """Minimum set of operations the application needs from an LLM backend."""

    @abstractmethod
    def generate(self, messages: list[Message]) -> str:
        """Return a complete, non-streamed response for the given messages."""

    @abstractmethod
    def stream(self, messages: list[Message]) -> Iterator[str]:
        """Yield response text incrementally for the given messages."""
