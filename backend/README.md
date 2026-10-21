# Backend

This directory contains the first FastAPI backend shell for the project.

## Current behavior

- `GET /health` returns `{"status": "ok"}` when the backend is available.
- `POST /api/reviews` accepts a validated `ReviewRequest` and returns deterministic
  mock/demo findings through the review service.
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
