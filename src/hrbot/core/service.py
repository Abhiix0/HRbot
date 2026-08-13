from hrbot.config import get_system_prompt
from hrbot.knowledge.retriever import KnowledgeRetriever
from hrbot.memory.store import append_assistant, append_user, get_history
from hrbot.providers.base import get_llm_response

retriever = KnowledgeRetriever()
retriever.load()


def get_response(user_input: str) -> str:
    append_user(user_input)
    history = get_history()
    system_prompt = get_system_prompt()
    
    # Augment prompt with knowledge
    knowledge = retriever.search(user_input)
    if knowledge:
        system_prompt += f"\n\nRelevant company knowledge:\n{knowledge}"
        
    response = get_llm_response(history, system_prompt)
    append_assistant(response)
    return response
