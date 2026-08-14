from __future__ import annotations

from collections.abc import Iterator

from hrbot.config import get_groq_api_key, get_model_name, get_system_prompt
from hrbot.knowledge.repository import KnowledgeRepository
from hrbot.knowledge.retriever import Retriever
from hrbot.memory.store import append_assistant, append_user, get_history
from hrbot.providers.base import LLMProvider, Message, ProviderError
from hrbot.providers.groq import GroqProvider

repo = KnowledgeRepository()
retriever = Retriever(repo)

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    """Lazily construct the configured LLM provider.

    Only this function (and tests) should know that "Groq" is the concrete
    implementation. Everything else talks to `LLMProvider`.
    """
    global _provider
    if _provider is None:
        _provider = GroqProvider(api_key=get_groq_api_key(), model=get_model_name())
    return _provider


def _build_messages(user_input: str) -> list[Message]:
    system_prompt = get_system_prompt()
    
    # Augment prompt with knowledge
    result = retriever.retrieve(user_input)
    if result.matches:
        knowledge = result.matches[0].entry.answer
        system_prompt += f"\n\nRelevant company knowledge:\n{knowledge}"

    messages = [Message(role="system", content=system_prompt)]
    messages.extend(get_history())
    messages.append(Message(role="user", content=user_input))
    return messages


def get_response(user_input: str) -> str:
    """Return a complete response, updating conversation memory."""
    messages = _build_messages(user_input)
    provider = get_provider()

    try:
        response = provider.generate(messages)
    except ProviderError:
        append_user(user_input)
        raise

    append_user(user_input)
    append_assistant(response)
    return response


def stream_response(user_input: str) -> Iterator[str]:
    """Stream a response chunk by chunk, updating conversation memory once done."""
    messages = _build_messages(user_input)
    provider = get_provider()

    chunks: list[str] = []
    try:
        for chunk in provider.stream(messages):
            chunks.append(chunk)
            yield chunk
    except ProviderError:
        append_user(user_input)
        raise

    append_user(user_input)
    append_assistant("".join(chunks))
