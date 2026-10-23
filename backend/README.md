# Backend

This directory contains the FastAPI backend for the local Python review assistant.

## Current behavior

- `GET /health` returns `{"status": "ok"}` when the backend is available.
- `POST /api/reviews` accepts a validated `ReviewRequest` and returns deterministic
  static-analysis findings through the mock/demo review service.
- Invalid requests return FastAPI validation errors, while unavailable or failing
  providers return a service-unavailable error.

The backend does not execute, import, compile, or send submitted Python code to a
shell. It does not call a real AI provider or store data.

## Local setup

Create and activate a project-local virtual environment from this directory:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Run the tests with:

```text
python -m pytest
```

Run the local API with:

```text
python -m uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`. Start the frontend separately from
the `frontend` directory; Vite proxies `/api` requests to this backend.

The backend currently analyzes submitted source as text only. It does not execute,
import, compile, shell out with, or persist submitted Python code.
