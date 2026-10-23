# Working Instructions for the Autonomous Code Review Agent

## Project purpose

This is a beginner-friendly portfolio project that reviews submitted Python source
code for possible bugs and security issues. The first version is a local web
application with a React frontend and a FastAPI backend.

## Scope boundaries

- Do not automatically execute, compile, import, or run submitted Python source code.
- Treat submitted code as untrusted input.
- Do not commit API keys, tokens, passwords, or other secrets.
- Keep the first version small and understandable. Do not add authentication,
  multi-user accounts, hosted deployment, or persistent storage unless the project
  requirements are updated first.
- Do not add automatic GitHub pull-request reviews to the first version.
- Label behavior that is heuristic or AI-generated rather than presenting it as
  guaranteed proof.
- Keep the mock/demo mode clearly labelled. Never present mock findings as real AI
  findings.
- Use deterministic mock/demo results for the first frontend-to-backend flow. Do not
  call a real AI provider until the AI integration milestone and its cost and data-use
  terms have been reviewed.
- Limit each submitted source file to an initial configurable maximum of 50 KB.
- Do not store submitted code or introduce a database in the initial version.
- Defer additional static-analysis tools until the basic application works.

## Development practices

- Read the relevant requirements and architecture documents before changing behavior.
- Prefer small, typed, testable modules with clear names.
- Validate input size, file type, and request shape at the application boundary.
- Treat frontend validation as user experience only; repeat every security-relevant
  validation in FastAPI.
- Keep the backend’s 50 KB source limit configurable and authoritative.
- Keep provider-specific AI code behind a small service interface so it can be
  replaced or tested without changing the UI.
- Keep any static-analysis integration separate from AI review and do not assume it
  belongs in the first release until the requirements are updated.
- Return structured review findings rather than parsing presentation text in the UI.
- Surface errors clearly; do not silently fall back to an empty review.
- Add or update focused tests for behavior changes.
- Run the smallest relevant formatter, linter, type checker, or test command before
  declaring a change complete.

## Security checklist

- Store configuration in environment variables and keep local secret files out of
  version control.
- Never place provider API keys in browser-delivered code.
- Enforce request and upload size limits.
- Sanitize or safely render returned Markdown/code; do not inject untrusted HTML.
- Use timeouts and bounded retries for external provider calls.
- Avoid logging submitted source code or secrets by default.
- Keep provider API keys and other secrets exclusively on the backend; never bundle
  them into the React application.

## Documentation

Keep `README.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, and
`docs/PLAN.md` consistent with implemented behavior. Mark assumptions, requested
scope, and optional future ideas separately.

## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues; use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Use the single-context root `GLOSSARY.md` and `docs/adr/`. See `docs/agents/domain.md`.
