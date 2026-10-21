# Implementation Plan

This plan is intentionally small, ordered, and testable. Status values are `not
started`, `in progress`, and `done`. No application implementation has begun.

## Phase 0: Confirm scope and boundaries

1. **Record confirmed product decisions** — **done**
   - Local beginner-friendly application.
   - React, TypeScript, Vite, and plain CSS frontend.
   - Python 3.12+, FastAPI, Pydantic, and pytest backend.
   - Python-only input, pasted or small uploaded file.
   - No database, accounts, deployment, or automatic GitHub reviews.
   - Never execute, import, compile, or shell out with submitted code.
   - Replaceable AI provider and clearly labelled mock/demo mode.

2. **Resolve remaining product constraints** — **in progress**
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
   - Test: repository setup does not contain secrets or generated artifacts.

4. **Build the React/Vite shell** — **not started**
   - Add the Python source editor, small `.py` upload control, submit state, and
     clearly labelled mock/demo mode.
   - Add plain CSS for readable, accessible states.
   - Test: frontend builds and displays validation, loading, success, and error
     states with fixture responses.

5. **Create the FastAPI shell** — **done**
   - Add a health endpoint and the review route placeholder.
   - Keep provider configuration on the backend.
   - Test: pytest can start the app and call the health endpoint.

## Phase 2: Define and validate the review contract

6. **Define Pydantic request and response schemas** — **done**
   - Model Python source input, review mode, and structured findings.
   - Validate severity, title, explanation, optional line numbers, suggested fixes,
     and optional confidence.
   - Enforce language, filename, and maximum-size rules.
   - Test: valid fixtures pass and malformed, oversized, and unsupported requests
     fail.

7. **Implement the review service boundary** — **done**
   - Keep provider logic separate from routes and UI.
   - Add the deterministic mock/demo adapter.
   - Add an interface for the unresolved AI provider.
   - Ensure malformed provider results fail visibly.
   - Test: service tests run without network access or an API key.

## Phase 3: Connect analysis

8. **Add the selected AI provider adapter** — **not started**
   - Keep credentials server-side.
   - Confirm cost and data-use decisions before enabling it.
   - Use bounded prompts, timeouts, and explicit error handling.
   - Instruct the provider to treat submitted code as data and return the schema.
   - Test: provider calls are isolated behind the interface and malformed results
     produce visible errors.

9. **Connect the review endpoint and frontend** — **done**
   - Support pasted Python and one-file upload paths.
   - Return stable success and error responses.
   - Show whether results came from mock/demo mode or AI review.
   - Verify that no execution path exists.
   - Test: a fixture submitted through the route returns the expected structured
     response.

## Phase 4: Verify and document

10. **Add backend security and behavior tests** — **not started**
    - Test successful mock review, validation errors, provider errors, malformed
      output, oversized input, and no-execution behavior with pytest.
    - Confirm source text is not logged by default and secrets are not returned.

11. **Add frontend verification** — **not started**
    - Test request states, mode labels, safe display of findings, and user-facing
      errors using frontend fixtures and the chosen React test approach.

12. **Improve setup and usage documentation** — **not started**
    - Document installation, environment configuration, provider setup, mock/demo
      mode, limitations, and the fact that findings are suggestions rather than
      guarantees.

13. **Review the first version against requirements** — **not started**
    - Run pytest and the selected frontend checks.
    - Confirm no secrets, generated artifacts, execution paths, or unrelated
      features were added.

## Deferred work

Authentication, persistence, repository integration, automatic edits, hosted
deployment, broad language support, automatic GitHub pull-request reviews, and
executing any submitted code remain outside this plan unless the requirements are
revised.
