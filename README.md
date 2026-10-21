# Autonomous Code Review Agent

An incremental portfolio project for learning how to build a code-review assistant.
The intended first version is a local web app: a user pastes or uploads a small
Python file, asks for a review, and receives structured findings about possible bugs
and security issues.

## Current status

This repository currently contains project documentation only. The application has
not been implemented, dependencies have not been installed, and no source code is
executed by the project.

Read these documents in order:

1. [Requirements](docs/REQUIREMENTS.md) - who the project serves and what it should do.
2. [Architecture](docs/ARCHITECTURE.md) - proposed stack, components, data flow, and
   security boundaries.
3. [Plan](docs/PLAN.md) - small implementation steps and their current status.
4. [Working instructions](AGENTS.md) - durable rules for future changes.

## Proposed first-version workflow

1. Start the local React/Vite frontend and FastAPI backend.
2. Paste Python source code or upload one small Python file.
3. Submit the review request from the frontend.
4. The frontend sends the source to FastAPI over a local HTTP request.
5. FastAPI validates the request, selects either mock/demo mode or the configured AI
   provider, and returns a validated structured response.
6. See findings grouped by severity, with a title, relevant line numbers when
   available, explanation, confidence where justified, and suggested fixes.
7. See a clear error if the input is too large, malformed, or the selected review
   mode is unavailable.

The submitted code is analyzed as text only. It is never automatically executed,
compiled, imported, passed to a shell, or imported by the backend.

## Confirmed technology stack

- **React**: builds the browser interface from reusable components.
- **TypeScript**: catches many frontend mistakes before the app runs and documents
  the shapes of frontend data.
- **Vite**: provides the frontend development server and production bundling.
- **Plain CSS**: styles the interface without adding a UI framework.
- **Python 3.12+**: powers the backend and review orchestration.
- **FastAPI**: exposes the local HTTP API and serves typed request handlers.
- **Pydantic**: validates backend requests and review responses.
- **pytest**: tests backend validation, review orchestration, provider boundaries,
  and safety behavior.
- **Git and GitHub**: track changes and host the portfolio repository.

The AI provider is intentionally not selected yet. The first working
frontend-to-backend flow will use mock review results only. Provider selection will
wait until the AI integration milestone, after reviewing provider costs and data-use
terms. A small provider interface will allow it to be replaced.

Each submitted source file is initially limited to **50 KB**. The backend will own
this configurable limit; the frontend may give earlier feedback but is not a
security boundary. The first version will not store submitted code or introduce a
database. Additional static-analysis tools are deferred until the basic application
works.

## Local setup

There is no dependency manifest or runnable application yet. Once implementation
begins, use two terminals from the repository root:

```text
cd frontend
npm install
npm run dev
```

```text
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

These commands describe the planned development workflow; the referenced files and
commands will be added in later milestones. Do not add secrets to this repository;
use backend-only environment configuration that is excluded from version control
once provider integration is implemented.

## Safety notes

- Never automatically execute submitted source code.
- Do not import or compile submitted source code, even for validation.
- Treat uploads and model output as untrusted data.
- Keep API keys on the server and out of browser code and logs.
- Display AI-generated findings as suggestions that require human review.
- Label mock/demo findings so they cannot be mistaken for AI-generated findings.
- The initial source-file limit is 50 KB and remains configurable on the backend.

## Current planning status

The repository contains planning documents only. Application code, package
installation, and implementation have not started. See
[docs/PLAN.md](docs/PLAN.md) for the ordered milestones and
[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) for unresolved decisions.
