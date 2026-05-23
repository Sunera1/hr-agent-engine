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

The orchestrator is the top-level entry point. The specialized agents are small and deterministic, with a mock LLM provider used to keep the prototype runnable without external keys.

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

Audit rows are append-only and stored in SQLite. Each request creates an initial `started` entry and then a final success or error entry. Failures are logged with user-safe messages instead of stack traces. This makes it possible to inspect what happened without allowing the audit endpoint to modify previous records.

## Failure Handling

The API catches workflow errors and returns a controlled error response. A scheduling request containing `force failure` is included so the fallback path can be tested locally. The mock LLM provider is enabled by default, so tests and endpoint checks do not depend on an external API.

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

## Future Improvements

- Add a richer intent model.
- Replace keyword retrieval with embeddings or a vector store.
- Add pagination to audit and memory endpoints.
- Add role-based access control.
- Expand observability with structured logging and metrics.

## Submission Note

This is a technical assessment prototype. It is designed for clarity, local execution, and review, not as a complete HR product.
