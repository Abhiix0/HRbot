import os
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    load_dotenv()


def get_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "system.txt"
    return prompt_path.read_text(encoding="utf-8").strip()


def get_groq_api_key() -> str | None:
    return os.getenv("GROQ_API_KEY")


def get_model_name() -> str:
    # .env historically stored this as "groq:llama-3.1-8b-instant" (a
    # pydantic-ai model string). Strip any "provider:" prefix so the value
    # works as a plain Groq model name too.
    raw = os.getenv("MODEL", "llama-3.1-8b-instant")
    return raw.split(":", 1)[-1] if ":" in raw else raw
