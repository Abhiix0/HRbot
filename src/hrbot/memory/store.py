from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic_ai.messages import ModelMessage

_history: list[dict] = []
_pai_history: list[ModelMessage] = []


def append_user(content: str) -> None:
    _history.append({"role": "user", "content": content})


def append_assistant(content: str) -> None:
    _history.append({"role": "assistant", "content": content})


def get_history() -> list[dict]:
    return list(_history)


def get_pai_history() -> list[ModelMessage]:
    return list(_pai_history)


def append_pai_messages(messages: list[ModelMessage]) -> None:
    _pai_history.extend(messages)


def clear() -> None:
    _history.clear()
    _pai_history.clear()
