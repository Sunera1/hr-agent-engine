# Technical Report

## Architecture

This project is a small FastAPI backend for routing HR-related requests. The API accepts a natural-language request, loads memory context from SQLite, classifies the intent, routes the request through a LangGraph workflow, stores memory and audit entries, and returns a structured response.

I kept the implementation at prototype level so it is easy to run and explain. It avoids background workers and extra services because they are not needed for the assessment scope.

## Endpoint Design

`GET /health` checks the app name and whether the SQLite database file exists.

`POST /request` runs the orchestration flow and returns `request_id`, `intent`, `confidence`, `routed_agent`, `memory_used`, `response`, and `status`.

`GET /audit` returns recent append-only audit records. No update or delete behavior exists for audit rows.

`GET /memory` returns STM and LTM memory, optionally filtered by `user_id`.

`DELETE /memory` clears STM and LTM memory, optionally filtered by `user_id`.

## Agent Flow

The LangGraph workflow follows this sequence:

1. Retrieve memory context.
2. Classify the request intent.
3. Route to the matching agent.
4. Save memory and compute significance.
5. Return the structured response.

The orchestrator is the top-level entry point. The specialized agents are small and deterministic, with a mock LLM provider used to keep the prototype runnable without external keys. A real OpenAI-compatible API or compatible local model server can be connected later through `.env` settings such as `MOCK_LLM`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `LLM_MODEL`.

Supported routing targets are:

- `scheduling_agent` for meetings, interviews, calendar requests, and availability.
- `leave_agent` for sick leave, PTO, vacation, and absence requests.
- `compliance_agent` for policy, audit, training, and compliance questions.
- `clarification_agent` when the request is empty, ambiguous, or below the confidence threshold.

## Memory Design

The project uses two memory tiers stored in SQLite.

STM stores recent interactions and is pruned to the configured limit. This gives the next few requests short-term context without keeping everything in the active context.

LTM stores significant entries that are likely to be useful later, such as policy-related requests or high-confidence leave/compliance items.

Retrieval ranks STM and LTM entries by simple token overlap with the current request plus a small weight for significance. This keeps retrieval explainable and easy to reason about.

## Significance Scoring Logic

The significance score is intentionally simple and transparent.

- A base score keeps every request above zero.
- The intent adds a bonus, with compliance weighted highest.
- The classifier confidence contributes a moderate boost.
- Keywords like policy, approved, urgent, repeat, tomorrow, and deadline add a small extra signal.

If the final score meets or exceeds `LTM_SIGNIFICANCE_THRESHOLD`, the memory item is also stored in LTM.

## Audit Log Design

Audit rows are append-only and stored in SQLite. Each request creates an initial `started` entry and then a final success or error entry. The code only exposes append and read operations for audit records, and SQLite triggers prevent direct update or delete operations on the `audit_log` table.

Each audit row stores `id`, `timestamp`, `user_id`, `request_text`, `classified_intent`, `confidence`, `routed_agent`, `memory_used`, `response_text`, `status`, and `error_message`.

## Retry, Timeout, and Fallback Handling

The orchestrator wraps workflow execution with `asyncio.wait_for`, using `REQUEST_TIMEOUT_SECONDS` from `.env`. It also supports a small retry loop through `AGENT_RETRY_ATTEMPTS`. This keeps the behavior easy to follow while still covering transient workflow failures.

Low-confidence classification is routed to the clarification agent instead of guessing. Other workflow errors return a polite fallback response and are written to the audit log without exposing raw Python stack traces. A scheduling request containing `force failure` is included so the fallback path can be tested locally. The mock LLM provider is enabled by default, so tests and endpoint checks do not depend on an external API.

## Trade-offs

- SQLite keeps the prototype easy to run but is not ideal for concurrent high-volume workloads.
- The classifier is deterministic rather than model-driven, which makes behavior repeatable but less flexible.
- The mock LLM provider makes local execution easy, but responses are only draft-style examples.
- The memory relevance logic is lightweight and explainable, but it is not semantic search.

## Known Limitations

- The system does not perform real HR actions.
- It does not connect to payroll, calendaring, or HRIS systems.
- The OpenAI-compatible provider is optional and not required for tests.
- The routing behavior is based on keywords and simple confidence heuristics.
- The audit and memory endpoints are not protected by authentication in this prototype.
- Depending on installed LangGraph/LangChain package versions, tests may show a non-blocking dependency warning. This does not affect the required API functionality or passing test results.

## Future Improvements

- Add a richer intent model.
- Replace keyword retrieval with embeddings or a vector store.
- Add pagination to audit and memory endpoints.
- Add role-based access control.
- Expand observability with structured logging and metrics.

## Bug Finding and Fixes

No separate starter code was present in this repository, so the checks focused on integration issues in the completed prototype. I verified imports, database initialization, endpoint names, FastAPI docs behavior, safe error handling, and the test suite.

Issues found and fixed during cleanup:

- Added `pytest.ini` so tests can import the local `app` package reliably.
- Added environment settings for `OPENAI_BASE_URL`, `LLM_MODEL`, and `AGENT_RETRY_ATTEMPTS`.
- Added simple retry handling around the LangGraph workflow.
- Added SQLite triggers to enforce append-only audit rows.
- Updated README and report wording so setup, endpoint coverage, LLM behavior, and limitations match the assessment requirements.

## Submission Note

This is a technical assessment prototype. It is designed for clarity, local execution, and review, not as a complete HR product.
