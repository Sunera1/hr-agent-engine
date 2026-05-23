# HR Agent Engine

Prototype HR request router built with FastAPI, LangGraph, SQLite, and a mock LLM provider.

The app is intentionally small so it can be reviewed and run locally. It uses mock HR data only and does not perform real HR actions.

## Overview

The service accepts a natural-language HR request, classifies the intent, routes it to a specialist agent, adds relevant memory context, stores an audit record, and returns a structured response.

Supported intents:

- scheduling
- leave
- compliance
- clarification

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

The default `.env.example` enables `MOCK_LLM=true`, so no real API key is required.

## Run

```powershell
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Endpoints

- `GET /health` returns service status and SQLite database connectivity.
- `POST /request` processes an HR request through the LangGraph workflow.
- `GET /audit` returns recent append-only audit entries.
- `GET /memory` returns STM and LTM memory, optionally filtered by `user_id`.
- `DELETE /memory` clears STM and LTM memory, optionally filtered by `user_id`.

## Sample Requests

### 1. Scheduling request

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_001\",\"message\":\"Please schedule a team interview next Tuesday at 2 PM\"}"
```

### 2. Leave request

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_001\",\"message\":\"I need to apply for sick leave tomorrow\"}"
```

### 3. Compliance request

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_003\",\"message\":\"What is the policy for completing compliance training on time?\"}"
```

### 4. Unclear request

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_004\",\"message\":\"Can you help me with this?\"}"
```

### 5. Request that uses memory

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_005\",\"message\":\"Please reschedule the interview we discussed earlier\"}"
```

### 6. Request that triggers fallback handling

```powershell
curl.exe -X POST http://127.0.0.1:8000/request -H "Content-Type: application/json" -d "{\"user_id\":\"user_006\",\"message\":\"Please schedule a meeting and force failure\"}"
```

### 7. Health, audit, and memory checks

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/audit
curl.exe http://127.0.0.1:8000/memory
curl.exe -X DELETE http://127.0.0.1:8000/memory
```

## Assumptions

- This is a prototype, not a production HR system.
- All HR content is synthetic and mock-only.
- SQLite is sufficient for the assessment scope.
- The classifier is deterministic and keyword-based for repeatable testing.
- The mock LLM provider is the default so the app runs without paid API keys.

## Testing

```powershell
pytest
```
