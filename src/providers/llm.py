import os

from pydantic_ai import Agent

from src.memory.history import get_pai_history, append_pai_messages


def get_llm_response(messages: list[dict], system_prompt: str) -> str:
    model = os.getenv("MODEL", "groq:llama-3.1-8b-instant")
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    prompt = user_messages[-1] if user_messages else ""
    agent = Agent(model, system_prompt=system_prompt)
    result = agent.run_sync(prompt, message_history=get_pai_history())
    append_pai_messages(result.new_messages())
    return result.output
