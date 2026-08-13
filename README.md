# test

An AI chatbot generated with Spawn, using Pydantic-Ai + Groq.

## Getting Started

1. Copy `.env.example` to `.env` and fill in your credentials:

```env
GROQ_API_KEY=your-key
```

2. Run the chatbot:

```bash
uv run python -m src.main
```

## Example

```
You: Hello
Bot: Hello! How can I help?
```

## Project Structure

```
test/
├── src/
│   ├── chatbot/      # Conversation orchestration
│   ├── providers/    # LLM provider (llm.py)
│   ├── prompts/      # system.txt
│   ├── memory/       # Runtime conversation history
│   ├── config/       # Settings and env loading
│   └── main.py
├── tests/
├── .env.example
└── README.md
```

## Running Tests

```bash
uv run pytest
```

## Roadmap (Not Yet Available)

```bash
spawn add rag
spawn add tools
spawn add vector-db
spawn add memory
spawn add mcp
spawn add voice
spawn add web-ui
spawn add streaming
spawn add observability
```
