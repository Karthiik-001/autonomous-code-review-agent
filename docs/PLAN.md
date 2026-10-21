# Implementation Plan

This plan is intentionally small, ordered, and testable. Status values are `not
started`, `in progress`, and `done`.

## Phase 0: Confirm scope and boundaries

1. **Record confirmed product decisions** — **done**
   - Local beginner-friendly application.
   - React, TypeScript, Vite, and plain CSS frontend.
   - Python 3.12+, FastAPI, Pydantic, and pytest backend.
   - Python-only input, pasted or small uploaded file.
   - No database, accounts, deployment, or automatic GitHub reviews.
   - Never execute, import, compile, or shell out with submitted code.
   - Replaceable AI provider and clearly labelled mock/demo mode.

2. **Resolve remaining product constraints** — **done**
   - Defer AI provider selection until the AI integration milestone.
   - Review API cost and data-use terms before calling a real provider.
   - Use a configurable 50 KB maximum per submitted source file initially.
   - Defer additional static-analysis tools until the basic application works.
   - Do not store submitted code or introduce a database.

## Phase 1: Establish the application shell

3. **Create the repository structure** — **done**
   - Add separate frontend and backend directories.
   - Add Git-safe ignore rules for dependencies, builds, and secrets.
   - Add concise development commands to the README.

4. **Build the React/Vite shell** — **done**
   - Python source editor, small `.py` upload control, submit state, and
     clearly labelled mock/demo mode.
   - Plain CSS for readable, accessible states.
   - Loading, error, success, and empty-result states.
   - Finding cards with severity badge, line number, explanation, suggested fix,
     and confidence.

5. **Create the FastAPI shell** — **done**
   - Health endpoint (`GET /health`) and review route (`POST /api/reviews`).
   - Provider configuration kept on the backend.
   - pytest can start the app and call the health endpoint.

## Phase 2: Define and validate the review contract

6. **Define Pydantic request and response schemas** — **done**
   - `ReviewRequest`: source, filename, language, mode with all validations.
   - `ReviewFinding`: severity, title, explanation, line numbers, suggested fix,
     confidence.
   - `ReviewResponse`: language, mode, findings list.
   - Valid fixtures pass; malformed, oversized, and unsupported requests fail.

7. **Implement the review service boundary** — **done**
   - `ReviewService` selects a provider, validates its output, and raises
     `ReviewServiceError` for failures.
   - `MockReviewProvider` delegates to `analyze_source()`.
   - `ReviewProvider` Protocol describes the adapter boundary.
   - Service tests run without network access or an API key.

## Phase 3: Connect analysis

8. **Implement the deterministic static checker** — **done**
   - `analyze_source()` in `backend/app/static_checks.py`.
   - Token-based detection of nine risk patterns (see README).
   - Handles malformed source, tokenization errors, multiline signatures, and
     explicit line continuation.
   - 11 focused unit tests, all passing.

9. **Connect the static checker to the review service** — **done**
   - `MockReviewProvider.review()` calls `analyze_source(request.source)`.
   - Service-level and HTTP-level tests verify real findings flow end to end.
   - Clean code returns an empty findings list.
   - 34 backend tests passing.

10. **Add the AI provider adapter** — **not started**
    - Keep credentials server-side.
    - Confirm cost and data-use decisions before enabling it.
    - Use bounded prompts, timeouts, and explicit error handling.
    - Instruct the provider to treat submitted code as data.
    - Planned first candidate: Ollama with a small quantized local model.

## Phase 4: Verify and document

11. **Update setup and usage documentation** — **done**
    - README updated with actual implementation status, setup instructions,
      checker reference table, architecture diagram, and limitations.
    - PLAN.md updated to reflect current milestone completion.

12. **Add frontend verification** — **not started**
    - Test request states, mode labels, safe display of findings, and user-facing
      errors using frontend fixtures and the chosen React test approach.

13. **Review the first version against requirements** — **not started**
    - Run pytest and the selected frontend checks.
    - Confirm no secrets, generated artifacts, execution paths, or unrelated
      features were added.

## Deferred work

Authentication, persistence, repository integration, automatic edits, hosted
deployment, broad language support, automatic GitHub pull-request reviews, and
executing any submitted code remain outside this plan unless the requirements are
revised.
