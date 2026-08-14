# Knowledge Base Schema

This document defines the canonical schema for all knowledge facts stored in the HR chatbot's knowledge base. Every fact, regardless of source, must conform to this structure.

## Overview

The knowledge base is a collection of `KnowledgeEntry` objects. Each entry answers a specific, narrowly-scoped question and is tagged with a fine-grained topic that maps cleanly to a single user question.

**Important:** The `topic` field is **more granular** than the source files. For example:
- `workplace.json` contains entries with multiple topic values: `"wfh_policy"`, `"office_access"`, `"it_laptop"`, `"it_account_setup"`, etc.
- `contacts.json` contains entries with topics like `"contact_hr"`, `"contact_it"`, etc.
- This prevents over-splitting and keeps related information together while maintaining clear semantic boundaries.

## Category-to-File Mapping

The task brief lists 7 fact categories; 6 files exist:

| Category | Storage Location | Notes |
|----------|------------------|-------|
| Company | `company.json` | General company info (mission, location, hours) |
| Onboarding | `onboarding.json` | First-day procedures, orientation |
| Leave | `leave.json` | Leave policies, balances, requests |
| Attendance | `attendance.json` | Check-in/out, timesheets, tardiness |
| Workplace | `workplace.json` | Office policies, WFH, access, AND all IT support (laptop, accounts, equipment) |
| Contacts | `contacts.json` | HR, IT, office admin contacts — information only |
| *(IT is consolidated)* | — | IT fact categories live in `workplace.json` for efficiency; IT's contact info lives in `contacts.json` |

## Schema Definition

### KnowledgeEntry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier. Format: `<topic>_<sequence>`, e.g. `"leave_casual_001"`, `"it_laptop_002"`. IDs must be unique across all knowledge files. |
| `topic` | string | Yes | Fine-grained topic tag. One topic = one clear question mapping. Examples: `"leave_casual"`, `"working_hours"`, `"wfh_policy"`, `"office_access"`, `"it_laptop"`, `"it_account_setup"`, `"contact_hr"`. |
| `keywords` | list[string] | Yes | Natural language keywords/phrases a user might search for. Include variations, synonyms, and informal phrasings. Must contain at least one keyword. Example: `["casual leave", "personal days", "taking time off"]`. |
| `question` | string | Yes | The canonical question this fact answers. Phrased as a complete question. Example: `"How many casual leave days do I get per year?"`. Must be non-empty. |
| `answer` | string | Yes | The grounded, complete-sentence answer safe to pass to an LLM as context. Must be a full, actionable answer. Example: `"Employees are entitled to 8 casual leave days per calendar year..."`. Must be non-empty. |
| `weight` | float | No | Importance/priority multiplier for relevance scoring. Default: `1.0`. Range: `0.5` to `2.0`. Higher values boost this fact in search results. |

## Example Entries

### Example 1: Leave Policy

```json
{
  "id": "leave_casual_001",
  "topic": "leave_casual",
  "keywords": ["casual leave", "personal days", "taking time off", "leave balance", "how much leave"],
  "question": "How many casual leave days do I get per year?",
  "answer": "Employees are entitled to 8 casual leave days per calendar year. These are subject to manager approval and must be submitted at least 2 business days in advance. Unused casual leave does not roll over to the next year.",
  "weight": 1.0
}
```

### Example 2: Working Hours

```json
{
  "id": "working_hours_001",
  "topic": "working_hours",
  "keywords": ["work hours", "office timing", "9 to 5", "when do I work", "start time", "end time"],
  "question": "What are the standard working hours?",
  "answer": "Standard working hours at NovaTech Solutions are 9:00 AM to 5:00 PM, Monday through Friday. Core hours are 10:00 AM to 3:00 PM when all team members are expected to be online. Flexible arrivals are permitted before 10:00 AM and departures after 3:00 PM, provided 8 hours are completed daily.",
  "weight": 1.0
}
```

### Example 3: IT Laptop Setup (topic nested in workplace.json)

```json
{
  "id": "it_laptop_001",
  "topic": "it_laptop",
  "keywords": ["laptop", "equipment", "hardware", "computer issue", "get a laptop", "laptop setup", "new device"],
  "question": "How do I get my laptop issued or set up?",
  "answer": "New hires receive a laptop on their first day during onboarding. If you need a replacement or additional hardware, submit a request through the IT support portal or email it-support@novatech.com. Turnaround is typically 2-3 business days. Ensure you first check the IT support contacts for quick troubleshooting.",
  "weight": 1.5
}
```

## Validation Rules

All `KnowledgeEntry` objects must pass these validations:

1. **id**: Must match pattern `^[a-z_]+_\d{3}$` (snake_case topic + underscore + 3-digit sequence).
2. **topic**: Non-empty string, must be a valid topic tag (lowercase, snake_case).
3. **keywords**: Non-empty list, each item is a non-empty string.
4. **question**: Non-empty string, should end with a question mark.
5. **answer**: Non-empty string, should be complete sentences (no abbreviations).
6. **weight**: Float, default 1.0, typically in range 0.5–2.0.

## Usage Notes

- **Retrieval**: Keywords are used by the retrieval system to match user queries against knowledge facts.
- **Scoring**: Weight is applied during relevance scoring to prioritize important facts.
- **Topic Tags**: Topic granularity is key — each topic should map to a distinct, answerable question. If two facts map to the same user question, they should share a topic or be consolidated.
- **No Duplication**: Each unique fact should have a unique ID and should not be repeated across files.
