from __future__ import annotations

from hrbot.providers.base import Message

_history: list[Message] = []


def append_user(content: str) -> None:
    _history.append(Message(role="user", content=content))


def append_assistant(content: str) -> None:
    _history.append(Message(role="assistant", content=content))


def get_history() -> list[Message]:
    return list(_history)


def clear() -> None:
    _history.clear()
