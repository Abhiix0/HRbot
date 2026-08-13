from src.providers.llm import get_llm_response
from src.memory.history import append_user, append_assistant, get_history
from src.config.settings import get_system_prompt


def get_response(user_input: str) -> str:
    append_user(user_input)
    history = get_history()
    system_prompt = get_system_prompt()
    response = get_llm_response(history, system_prompt)
    append_assistant(response)
    return response
