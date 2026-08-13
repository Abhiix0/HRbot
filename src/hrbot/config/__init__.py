from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    load_dotenv()


def get_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "system.txt"
    return prompt_path.read_text(encoding="utf-8").strip()
