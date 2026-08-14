from hrbot.config import get_system_prompt
from hrbot.knowledge.repository import KnowledgeRepository
from hrbot.knowledge.retriever import Retriever
from hrbot.memory.store import append_assistant, append_user, get_history
from hrbot.providers.base import get_llm_response

repo = KnowledgeRepository()
retriever = Retriever(repo)


def get_response(user_input: str) -> str:
    append_user(user_input)
    history = get_history()
    system_prompt = get_system_prompt()
    
    # Augment prompt with knowledge
    result = retriever.retrieve(user_input)
    if result.matches:
        knowledge = result.matches[0].entry.answer
        system_prompt += f"\n\nRelevant company knowledge:\n{knowledge}"
        
    response = get_llm_response(history, system_prompt)
    append_assistant(response)
    return response
