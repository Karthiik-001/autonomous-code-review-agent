# Architecture

## Design goals

The architecture favors a small number of understandable components, explicit data
validation, and a hard boundary between submitted text and any execution
environment. The first version is stateless, runs locally, and supports Python only.

## Technology choices

### Confirmed stack

- **React** organizes the frontend into components such as the source editor, upload
  control, review button, status messages, and findings list.
- **TypeScript** gives the frontend explicit types for requests, responses, and UI
  state.
- **Vite** supplies the frontend development server and bundles the browser code.
- **Plain CSS** keeps styling understandable without adding a UI framework.
- **Python 3.12+** provides the backend language and review orchestration.
- **FastAPI** exposes the local HTTP API.
- **Pydantic** validates request data and provider responses on the backend.
- **pytest** tests backend behavior without requiring a live provider.
- **Git and GitHub** provide version history, collaboration, and portfolio hosting.
- **A replaceable provider interface** isolates the unresolved AI provider choice.
- **A mock/demo provider** enables a clearly labelled no-key flow.
- **No database** is used because the first version does not persist reviews.
- **A configurable 50 KB input limit** bounds each submitted source file initially.

### Alternatives

- **Django** provides more batteries-included features, but is more framework than
  this first version needs.
- **A local model** can reduce external data sharing but adds setup and hardware
  complexity.
- **A Python template frontend** would reduce frontend tooling, but does not match
  the confirmed React and TypeScript learning goals.

These alternatives are not requirements. The confirmed stack should be revisited only
if the project requirements change.

## Components

```text
React + TypeScript + Vite
   |
   | local HTTP request
   v
FastAPI route layer
   |
   +--> Backend input validation and normalization
   |
   +--> Review service interface
           |
           +--> AI provider adapter (external API, unresolved choice)
           +--> Deterministic mock/demo adapter
   |
   +--> Pydantic response validation
   |
   v
Structured review response
```

### React frontend

Provides the paste area, Python file picker, submit state, findings display, demo
mode label, and error messages. TypeScript types the API data. Frontend validation
improves usability by catching obvious empty or oversized input before a request, but
it is not a security boundary and can be bypassed.

### FastAPI route layer

Accepts the request, repeats all important validation, enforces content and size
limits, calls the review service, and returns a stable response shape. It does not
contain provider prompt logic.

### Review service

Owns the use case: build a bounded review request, call the selected adapter, validate
the result, and return findings. A provider adapter is injected so tests do not need
network access.

### Provider adapters

The AI adapter translates between the application’s review schema and a
provider-specific API. It uses backend-only environment configuration, a timeout,
bounded retry behavior, and structured output validation. The mock/demo adapter
returns deterministic, clearly labelled sample findings without a provider key.
Neither adapter executes, imports, compiles, or sends submitted code to a shell.

### AI review versus static analysis

AI review asks a model to reason about source text and explain possible issues. It is
probabilistic and can miss issues or make mistakes. Static analysis uses deterministic
rules or language-aware tools to inspect code without executing it. Static analysis
can provide repeatable checks, but any extra tool is unresolved for the first release
and must not be added by assumption.

## React-to-FastAPI request flow

1. The React frontend validates obvious user errors and builds a request containing
   Python source text and filename.
2. The frontend sends the request to the local FastAPI endpoint.
3. FastAPI repeats validation, including non-empty content, Python file handling, and
   the maximum size.
4. The review service uses the deterministic mock/demo adapter for the first working
   flow. It does not call a real AI provider yet.
5. At a later AI integration milestone, the selected adapter will create an
   instruction that treats the source as data, not as instructions, and requests
   only the defined structured schema.
6. The active adapter result is parsed and validated with Pydantic.
7. The service rejects malformed findings rather than returning a success-shaped
   fallback.
8. FastAPI returns the validated response to the React frontend.
9. The frontend safely displays findings and suggested fixes, including the mode
   label.

No step invokes a shell, interpreter, compiler, import mechanism, plugin, or
third-party execution service on submitted code.

## Initial API

### `GET /health`

Returns a simple backend health response for local development and tests.

### `POST /api/reviews`

Accepts a multipart upload or a JSON request containing:

- `source`: Python source code text;
- `filename`: optional display name;
- `language`: `python` in the first version;
- `mode`: `mock`/`demo` or configured `ai` review.

Returns a response containing the language, review mode, and an array of findings.
Each finding includes severity, title, explanation, optional line numbers, optional
suggested fixes, and optional confidence.

Expected error categories include invalid input (`4xx`), provider timeout or
unavailability (`5xx` or a clearly mapped service error), and invalid provider
output. Error responses should have a stable, user-safe message and an internal
correlation identifier if logging is introduced.

## Database decision

No database is needed initially. The app should not retain source code or review
results after the request. If review history becomes a requested feature, add SQLite
behind a repository interface, define retention behavior, and review privacy and
deletion requirements before implementing it.

## Security boundaries

- Source code is untrusted input and is never executed.
- Source code is never imported, compiled, or passed to a shell.
- Each source file is limited to an initial configurable maximum of 50 KB.
- Request body and upload limits prevent accidental resource exhaustion.
- File names are display metadata only; they are not used as paths or commands.
- API keys are server-only environment configuration and never enter the frontend
  bundle.
- Logs should omit source contents and credentials.
- Provider output is untrusted and must be schema-validated and safely rendered.
- Network calls use HTTPS, timeouts, bounded retries, and explicit error handling.
- Frontend validation is never treated as a substitute for backend validation.
- If a hosted deployment is later added, authentication, rate limits, quotas, CSRF
  protection, and data-retention rules become mandatory design work.

## Test seams

- Route tests can use an injected fake review service.
- Review service tests can use a fake provider response.
- Schema tests can cover valid findings, malformed output, unknown severities, and
  missing locations.
- Safety tests should verify that source text is never passed to an execution API and
  that the UI does not render arbitrary HTML.
- Frontend tests, when added, should verify mode labels and request/error states.

## Unresolved architecture decisions

- Select the first AI provider.
- Define acceptable API cost limits and review the provider’s data-use terms.
- Set the exact maximum input size.
- Decide whether additional static-analysis tools belong in the first release.
- Keep submitted code transient; do not add a database or code storage.
