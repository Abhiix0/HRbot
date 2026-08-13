import pytest

from src.memory.history import clear


@pytest.fixture(autouse=True)
def reset_memory():
    """Reset conversation history before every test."""
    clear()
    yield
    clear()
