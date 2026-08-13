# Architecture

## Overview
NovaTech HR CLI (`hrbot`) is an AI assistant.

## Flow
1. **CLI (`cli/app.py`)**: Entry point, gets user input.
2. **Service (`core/service.py`)**: Orchestrator.
3. **Knowledge (`knowledge/retriever.py`)**: Retrieves documents to augment the prompt.
4. **Memory (`memory/store.py`)**: Manages conversation history.
5. **Provider (`providers/base.py`)**: Calls the LLM.
