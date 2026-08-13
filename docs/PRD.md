# NovaTech HR Onboarding CLI Assistant

## Product Requirements Document v0.1

**Project Type:** Micro Project
**Interface:** Terminal / CLI
**Status:** Draft
**Target Build Time:** 1–2 days
**Company:** NovaTech Solutions
**Location:** Hyderabad, India
**Primary Users:** New employees

---

# 1. Product Overview

NovaTech HR Onboarding CLI Assistant is a terminal-based AI assistant designed to help new employees quickly find answers to common HR and onboarding questions.

The assistant uses a small, controlled JSON knowledge base containing NovaTech's fictional company policies, onboarding information, contacts, workplace rules, and other relevant information.

The system retrieves relevant information from the knowledge base before asking the LLM to generate the final response.

The v0 application runs entirely from the terminal and maintains conversation history only for the current process.

---

# 2. Problem Statement

New employees frequently have repetitive questions during their first days and weeks at a company.

Examples include:

* What are the working hours?
* How many casual leaves do I get?
* What documents are required for onboarding?
* How do I apply for leave?
* What is the work-from-home policy?
* Who should I contact for an HR issue?
* When will I receive my employee ID?

These questions are individually simple but create unnecessary interruptions for HR teams when employees need to ask them repeatedly.

The product aims to provide a fast self-service interface for these routine questions without requiring direct HR interaction for every query.

---

# 3. Target User

## Primary User

**New employee at NovaTech Solutions.**

The user is assumed to:

* Be unfamiliar with company processes.
* Have basic terminal access.
* Need quick answers to routine onboarding questions.
* Not have direct access to internal HR systems through the application.

The v0 system does **not** distinguish between individual employees or expose employee-specific information.

---

# 4. Product Goal

The core product goal is:

> Allow a new employee to obtain accurate answers to common HR and onboarding questions through a simple terminal interface.

The system should optimize for:

* Accuracy
* Fast responses
* Clear answers
* Controlled knowledge
* Graceful refusal when information is unavailable
* Useful conversational context
* Simple user experience

---

# 5. Success Criteria

The v0 is successful when a user can:

1. Start the assistant from the terminal.
2. Ask natural-language HR questions.
3. Receive answers grounded in the JSON knowledge base.
4. Ask contextual follow-up questions.
5. Clear and inspect the current conversation.
6. Receive streamed responses.
7. Recover gracefully from provider or input failures.
8. Exit without Python tracebacks.
9. Run the project's automated tests successfully.
10. Run the AI evaluation suite successfully.

---

# 6. Scope

## 6.1 In Scope

### CLI Application

* Interactive terminal chat.
* Clean colored terminal output.
* Rich-based formatting where useful.
* Streaming model responses.
* CLI commands.
* Graceful Ctrl+C and Ctrl+D handling.

### Knowledge

* Structured JSON knowledge base.
* Approximately 20–50 facts.
* Target approximately 35 facts.
* Company information.
* Working hours.
* Attendance.
* Leave policies.
* Onboarding requirements.
* WFH/hybrid policy.
* IT/equipment information.
* HR contacts.
* Payroll basics.
* Workplace/emergency procedures.

### AI

* Groq as the implemented LLM provider.
* Llama 3.1 8B Instant.
* Provider abstraction.
* Context-aware responses.
* Controlled answer generation.
* Hallucination/refusal behavior.

### State

* Current-session conversation history.
* In-memory storage only.
* Conversation clearing.
* Conversation history inspection.

### Engineering

* Automated tests.
* Lightweight structured logging.
* AI evaluation dataset.
* Ruff.
* Type checking.
* Pytest.
* GitHub Actions CI.

---

# 7. Explicitly Out of Scope

The following will **not** be implemented in v0:

* Web interface.
* Mobile application.
* HRMS integration.
* Payroll integration.
* Employee-specific HR data.
* Authentication.
* Employee accounts.
* Leave submission.
* Leave approval.
* Database persistence.
* Long-term conversation memory.
* Vector database.
* Embeddings.
* Full RAG pipeline.
* Multiple implemented LLM providers.
* Ollama/local inference.
* Docker.
* Cloud deployment.
* Admin dashboard.
* Admin CMS.
* Webhooks.
* Multi-language support.
* Voice interface.

These features may appear in the future roadmap but are not part of the v0 implementation.

---

# 8. Example User Questions

The assistant should be able to handle questions such as:

```text
What are the working hours?

How many casual leaves do I get?

What documents do I need to complete onboarding?

How do I apply for leave?

What is the work-from-home policy?

Where can I find the employee handbook?

Who do I contact for HR-related issues?

When do I get my employee ID?

What is the attendance policy?

Who do I contact if I have a laptop or IT issue?
```

The system should also support natural variations of these questions.

For example:

```text
What time does work start?

When should I be at the office?

How much casual leave am I entitled to?

Where do I go if my laptop isn't working?
```

---

# 9. Company Context

The assistant operates against a fictional company dataset.

## NovaTech Solutions

| Attribute     | Value                 |
| ------------- | --------------------- |
| Industry      | Software & Technology |
| Employees     | ~500                  |
| Location      | Hyderabad, India      |
| Work Model    | Hybrid                |
| Office Hours  | 9:30 AM – 6:30 PM     |
| Primary Users | New employees         |

The company information exists only to provide realistic context for the micro-project.

---

# 10. Knowledge Base

## 10.1 Source

The v0 knowledge base will use **JSON files**.

No database is required.

Example conceptual structure:

```text
knowledge/
├── company.json
├── onboarding.json
├── leave.json
├── attendance.json
├── workplace.json
└── contacts.json
```

The exact file structure may be simplified during implementation if multiple files provide no practical benefit.

---

# 11. Knowledge Retrieval

The assistant must not blindly send every user question directly to the LLM and ask it to answer from its own knowledge.

Instead, the intended flow is:

```text
User Question
      │
      ▼
Question Processing
      │
      ▼
Topic / Relevant Knowledge Identification
      │
      ▼
JSON Knowledge Retrieval
      │
      ▼
Relevant Context
      │
      ▼
LLM
      │
      ▼
Final Response
```

The v0 retrieval mechanism should remain simple.

Possible approaches include:

* keyword matching
* topic classification
* metadata matching
* lightweight scoring

The implementation should choose the simplest mechanism that reliably retrieves the relevant knowledge.

The project must **not introduce embeddings or vector search merely for the sake of calling the system RAG**.

---

# 12. Grounded Response Generation

The LLM should generate responses using the retrieved knowledge as its authoritative context.

Conceptually:

```text
User:
"What are the working hours?"

        ↓

Retriever

        ↓

Relevant knowledge:
"NovaTech working hours are
9:30 AM – 6:30 PM."

        ↓

LLM

        ↓

"NovaTech's standard working hours
are 9:30 AM to 6:30 PM."
```

The LLM should not invent missing policy information.

---

# 13. Unknown Information / Hallucination Boundary

If the knowledge base does not contain sufficient information to answer a question, the assistant must not fabricate an answer.

Example:

```text
You > What is NovaTech's maternity leave policy?

Bot > I don't have information about NovaTech's maternity
      leave policy in my current knowledge base.
```

The system should internally record that the query could not be confidently answered.

This behavior is a core product requirement, not an optional prompt instruction.

---

# 14. Confidence

The v0 should track retrieval confidence internally.

The numerical confidence value should **not** be shown to users.

Conceptually:

```text
Strong retrieval
      ↓
Generate grounded answer

Weak retrieval
      ↓
Do not guess
      ↓
Return controlled refusal
```

The exact confidence calculation is an implementation detail and should be selected based on the chosen retrieval strategy.

---

# 15. Conversation Memory

The assistant should maintain short-term conversation context.

Example:

```text
You > What are the working hours?

Bot > NovaTech's working hours are 9:30 AM
      to 6:30 PM.

You > What about Friday?

Bot > Friday follows the same standard working hours.
```

Conversation history exists only for the current process.

When the application exits:

```text
memory → discarded
```

No database or persistent file storage is required.

---

# 16. CLI Commands

The CLI should support the following commands.

| Command    | Behavior                             |
| ---------- | ------------------------------------ |
| `/help`    | Show available commands              |
| `/clear`   | Clear current conversation           |
| `/history` | Display current conversation history |
| `/about`   | Display application information      |
| `/quit`    | Exit the application                 |

Commands must be processed by the CLI layer and should **not** be sent to the LLM as user messages.

---

# 17. CLI Experience

The terminal should provide a clean, readable interface without attempting to become a full terminal UI framework.

Example:

```text
╭────────────────────────────────────────╮
│     NovaTech HR Onboarding Assistant   │
╰────────────────────────────────────────╯

Type /help for available commands.

You > What are the working hours?

Bot > NovaTech's standard working hours are
      9:30 AM to 6:30 PM.
```

Rich may be used selectively for:

* formatting
* colors
* panels
* tables
* status indicators
* streaming output

Visual complexity should remain secondary to application behavior.

---

# 18. Streaming

LLM responses should be streamed to the terminal where supported by the provider/runtime.

Expected interaction:

```text
You > What is the WFH policy?

Bot > NovaTech follows a hybrid work model...
```

The application should not block the user behind an unnecessarily opaque loading state when streaming is available.

---

# 19. Input and Exit Handling

The application must handle normal terminal interruptions cleanly.

### Ctrl+C

Expected behavior:

```text
^C

Session closed.
```

No Python traceback should be displayed.

### Ctrl+D

Ctrl+D should be treated as end-of-input and terminate the session cleanly.

Unexpected exceptions should still be logged appropriately rather than silently swallowed.

---

# 20. LLM Architecture

The application should not directly couple the conversation layer to Groq.

Required conceptual boundary:

```text
Application
     │
     ▼
LLMProvider
     │
     ▼
GroqProvider
     │
     ▼
Groq
     │
     ▼
Llama 3.1 8B Instant
```

Only the Groq implementation is required for v0.

The provider boundary exists so another provider can be added later without rewriting the conversation and CLI layers.

---

# 21. Configuration

Configuration should be separated from application logic.

At minimum, configuration should cover:

* LLM provider.
* Model.
* API key.
* Application environment.
* Logging level where required.

Secrets must come from environment variables or an equivalent local configuration mechanism.

API keys must never be committed to the repository.

---

# 22. Application Architecture

The system should maintain clear boundaries between:

```text
CLI
 │
 ▼
Conversation Core
 │
 ├──────────────► Memory
 │
 ├──────────────► Knowledge Retrieval
 │
 └──────────────► LLM Provider
                         │
                         ▼
                       Groq
```

### CLI Layer

Responsible for:

* input
* commands
* terminal output
* interruption handling

### Conversation Core

Responsible for:

* processing user messages
* coordinating retrieval
* maintaining conversation context
* requesting model responses

### Knowledge Layer

Responsible for:

* loading JSON
* retrieving relevant information
* determining retrieval strength

### Memory Layer

Responsible for:

* storing current-session messages
* retrieving history
* clearing history

### Provider Layer

Responsible for:

* communicating with the LLM provider
* streaming responses
* provider-specific behavior
* translating provider failures into application-level errors

The LLM provider must not own CLI behavior.

---

# 23. Error Handling

The application should explicitly handle at least:

### Provider failures

Examples:

* API unavailable
* timeout
* authentication failure
* rate limit

The user should receive a useful error message rather than a traceback.

### Knowledge failures

Examples:

* malformed JSON
* missing knowledge file
* invalid knowledge structure

These should fail clearly and be logged.

### User input

Examples:

* empty input
* whitespace-only input
* unsupported command

The application should handle these without crashing.

---

# 24. Logging

The project will use Python's standard `logging` infrastructure.

Important events should be logged at appropriate levels.

### INFO

```text
session_started
request_started
response_completed
session_closed
```

### WARNING

```text
knowledge_not_found
low_retrieval_confidence
unsupported_command
```

### ERROR

```text
provider_failure
knowledge_load_failure
unexpected_application_error
```

Logs should provide useful diagnostic information without leaking secrets or unnecessary user data.

---

# 25. Testing Strategy

Testing should focus on behavior and boundaries rather than implementation trivia.

## CLI

Test:

* command parsing
* `/help`
* `/clear`
* `/history`
* `/about`
* `/quit`
* empty input
* Ctrl+C behavior
* Ctrl+D behavior

## Knowledge

Test:

* valid knowledge loading
* retrieval of known topics
* unknown questions
* low-confidence retrieval
* malformed knowledge data

## Conversation

Test:

* message flow
* conversation history
* contextual follow-ups
* clearing history

## Provider

Test:

* successful responses
* streaming behavior where practical
* provider failures
* timeout/error handling

## Safety

Test that:

```text
unknown information
       ↓
controlled refusal
```

rather than:

```text
unknown information
       ↓
fabricated answer
```

Provider calls should be mocked in unit tests so tests do not depend on live Groq requests.

---

# 26. AI Evaluation

The project should include a small evaluation dataset separate from normal unit tests.

Each evaluation case should contain conceptually:

```text
Question
Expected topic
Expected knowledge entry/source
Expected behavior
```

Examples:

```text
"What time does the workday start?"
→ working_hours
→ should_answer

"How many casual leaves are available?"
→ leave
→ should_answer

"What is the maternity leave policy?"
→ no_matching_knowledge
→ should_refuse
```

The project should expose an evaluation command:

```text
uv run evaluate
```

The evaluation should report useful metrics such as:

* retrieval accuracy
* answerable-question success rate
* refusal correctness
* unknown-question handling

The evaluation system should remain lightweight and deterministic where possible.

---

# 27. Dependencies

The v0 dependency set should remain intentionally small.

Expected core tooling:

```text
Python
Pydantic AI
Groq integration
Rich
Pytest
Ruff
Type checker
```

The exact packages should be finalized during implementation.

No dependency should be introduced solely because it is fashionable or because a larger architecture might eventually need it.

---

# 28. CI

GitHub Actions should run on pushes and pull requests.

Minimum pipeline:

```text
Checkout
   ↓
Install dependencies
   ↓
Ruff
   ↓
Type checking
   ↓
Pytest
```

AI evaluation may be added as a separate CI stage once it can run deterministically without requiring a live model API.

Secrets must not be exposed to pull-request builds from untrusted sources.

---

# 29. Packaging / Execution

The primary user experience should be:

```bash
uv run hrbot
```

The CLI should be exposed through the project's Python package configuration rather than requiring users to manually execute `main.py`.

The project should be installable and runnable from a clean environment using the documented setup instructions.

---

# 30. Repository Expectations

The repository should contain at minimum:

```text
project/
├── src/
├── tests/
├── knowledge/
├── prompts/
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
└── uv.lock
```

The exact internal module structure will be finalized during implementation.

The README should explain:

* what the project does
* architecture
* setup
* environment variables
* running the CLI
* available commands
* testing
* evaluation
* limitations
* future roadmap

---

# 31. Security Requirements

Even though v0 is a local CLI application, basic security discipline is required.

The application must:

* never commit API keys
* load secrets from environment/configuration
* avoid logging secrets
* avoid unnecessarily logging complete user conversations
* treat retrieved knowledge as controlled application data
* never claim access to employee-specific systems
* never fabricate employee-specific information

No authentication system is required for v0.

---

# 32. Performance Expectations

The application should feel responsive for a CLI application.

Primary performance concern is LLM/provider latency.

The application should:

* stream responses where possible
* avoid unnecessary repeated knowledge loading
* avoid creating redundant provider/model state per message
* maintain conversation state efficiently in memory

No formal high-load benchmark is required for v0.

---

# 33. Development Constraints

The project is intentionally limited to a **1–2 day micro-project**.

Therefore:

### Build

```text
CLI
+
JSON knowledge
+
retrieval
+
LLM
+
memory
+
commands
+
streaming
+
error handling
+
tests
+
evaluation
+
logging
+
CI
```

### Do not build

```text
Web UI
Database
Vector DB
Embeddings
RAG framework
Authentication
HRMS
Docker
Kubernetes
Multi-provider runtime
Ollama runtime
Admin dashboard
```

The project should prefer **depth of implementation over breadth of features**.

---

# 34. Acceptance Criteria

The v0 is considered complete when all of the following are true:

### Core

* [ ] Application starts successfully through the documented CLI command.
* [ ] User can ask natural-language HR questions.
* [ ] Relevant JSON knowledge is retrieved.
* [ ] LLM generates responses using retrieved knowledge.
* [ ] Unknown information results in a controlled refusal.
* [ ] Conversation context is maintained during the session.

### CLI

* [ ] `/help` works.
* [ ] `/clear` works.
* [ ] `/history` works.
* [ ] `/about` works.
* [ ] `/quit` works.
* [ ] Responses stream correctly.
* [ ] Ctrl+C exits cleanly.
* [ ] Ctrl+D exits cleanly.
* [ ] No traceback appears during normal user exits.

### Engineering

* [ ] Groq is isolated behind a provider abstraction.
* [ ] Configuration is separated from business logic.
* [ ] Knowledge loading and retrieval are independently testable.
* [ ] Provider calls are mockable.
* [ ] Errors are handled at appropriate boundaries.
* [ ] Logging is implemented.
* [ ] Secrets are not committed.

### Quality

* [ ] Unit/behavioral tests pass.
* [ ] Ruff passes.
* [ ] Type checking passes.
* [ ] GitHub Actions passes.
* [ ] AI evaluation can be executed locally.
* [ ] README documents setup and usage.

---

# 35. Future Roadmap

The following are intentionally deferred.

## v1

Potential additions:

* Better retrieval strategy.
* More structured knowledge metadata.
* Persistent local conversations.
* Source references in answers.
* Improved evaluation dataset.

## v2

Potential additions:

* Embedding-based retrieval.
* Proper RAG pipeline.
* Larger document knowledge base.
* Knowledge freshness/versioning.

## v3

Potential additions:

* Local Ollama provider.
* Additional LLM providers.
* Employee authentication.
* Employee-specific information.

## v4

Potential additions:

* HRMS integration.
* Leave actions.
* Web interface.
* Administrative knowledge management.

These are roadmap possibilities, **not commitments**.

---

# 36. Product Principle

The central principle of the project is:

> **Retrieve first. Generate second. Refuse when unsupported.**

The assistant should never confuse the language model's ability to produce an answer with the application's ability to know that answer.

The LLM is responsible for **communicating information**.

The knowledge system is responsible for **providing information**.

The application is responsible for **deciding how those pieces interact safely**.

That separation is the core engineering lesson of the project.

---

# 37. Final v0 Definition

NovaTech HR Onboarding CLI Assistant is a small, terminal-native AI application that demonstrates how to build a structured AI system without hiding everything behind a single LLM API call.

The final v0 pipeline is:

```text
                 ┌─────────────────┐
                 │   Terminal CLI  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Input / Command │
                 │     Parser      │
                 └────────┬────────┘
                          │
                    user message
                          │
                          ▼
                 ┌─────────────────┐
                 │ Conversation    │
                 │     Core        │
                 └───────┬─┬───────┘
                         │ │
              ┌──────────┘ └──────────┐
              ▼                       ▼
       ┌──────────────┐       ┌──────────────┐
       │ Conversation │       │  Knowledge   │
       │    Memory    │       │  Retrieval   │
       └──────────────┘       └──────┬───────┘
                                     │
                              relevant context
                                     │
                                     ▼
                              ┌─────────────┐
                              │ LLM Provider│
                              │   Groq      │
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   Response  │
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │ Terminal UI │
                              └─────────────┘
```

**That's the project.**

Small enough to finish in two days. Serious enough to demonstrate actual AI application engineering. No architectural theme park. 🔧
