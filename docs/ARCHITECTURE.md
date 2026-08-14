# Architecture

## Overview
NovaTech HR CLI (`hrbot`) is an AI assistant.

## Flow
1. **CLI (`cli/app.py`)**: Entry point, gets user input.
2. **Service (`core/service.py`)**: Orchestrator.
3. **Knowledge (`knowledge/retriever.py`)**: Retrieves documents to augment the prompt.
4. **Memory (`memory/store.py`)**: Manages conversation history.
5. **Provider (`providers/base.py`)**: Calls the LLM.

## ⚠️ P3 Integration Note

**Stale interface in `core/service.py`:**  
The current `service.py` calls `retriever.search()` which no longer exists and expects a plain string return.
As of Phase 2, the new interface is:
- Public entry points: `KnowledgeRepository.load()` and `Retriever.retrieve(query)`
- `Retriever.retrieve(query)` returns `RetrievalResult(matches, top_score, confidence)` instead of a string

The P3 Conversation Core integration should update `service.py` to use the new interface and handle the `RetrievalResult` contract.
