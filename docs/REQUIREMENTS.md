# Requirements

## Purpose

The project is a learning-focused portfolio application that demonstrates how a
developer can submit Python source code and receive an understandable review of
possible bugs and security issues. It should teach the builder about React-to-API
requests, input validation, provider integration, structured output, and safe
handling of untrusted content.

## Intended users

### Primary user

A beginner developer who wants a readable explanation of possible issues in a small
piece of source code.

### Secondary user

A portfolio reviewer or fellow developer evaluating whether the project has a clear
architecture, sensible security precautions, useful tests, and understandable UX.

## Requested first-version behavior

### Input

- A user can paste Python source code into a React form.
- A user can upload one small Python source file.
- Python is the only supported review language in the first version.
- The application validates that input exists and is no larger than the initial
  configurable 50 KB per-file limit.
- The application rejects unsupported or malformed requests with a useful message.
- The frontend provides immediate usability feedback, but backend validation remains
  authoritative.

### Review

- The application analyzes code as text.
- The review requests possible bugs and security issues, not a claim of formal
  correctness or complete vulnerability coverage.
- The review asks for evidence from the submitted code and avoids inventing file
  locations.
- The provider response is validated into a known schema before it is shown.
- The first working frontend-to-backend flow uses a clearly labelled mock/demo mode
  that returns deterministic sample findings without an AI API key.
- Mock/demo findings must never be presented as real AI findings.
- A real AI provider is not called before the AI integration milestone.

### Output

Each finding should support:

- severity: `critical`, `high`, `medium`, `low`, or `info`;
- a concise title;
- relevant source line numbers when they can be identified;
- a plain-language explanation;
- a suggested correction or safer code example when appropriate;
- a confidence indicator when justified.

The UI should also show the reviewed language and a clear empty-result state when no
issues are identified. “No findings” must not be presented as proof that the code is
safe.

### Errors and safety

- Provider failures, timeouts, invalid provider output, and validation failures are
  visible to the user.
- The app never executes, compiles, imports, or evaluates submitted code.
- API keys are read only by the server from environment configuration.
- Source code and secrets are not logged by default.
- Returned Markdown or code is rendered safely without arbitrary HTML injection.

## Non-goals for the first version

- User accounts, authentication, or authorization.
- Multi-user collaboration.
- Persistent review history or a database.
- Repository integration, pull requests, or CI/CD checks.
- Automatic code changes or commits.
- Running tests, linters, compilers, interpreters, or sandboxes on submitted code.
- Adding third-party static-analysis tools before deciding that they belong in the
  first release.
- Guaranteed vulnerability detection, formal verification, or compliance
  certification.
- Supporting languages other than Python.
- A hosted production deployment.

## Optional future ideas

These are deliberately deferred until the first workflow is useful and tested:

- A small set of language-specific static checks, if they are chosen after the
  first-release decision.
- Review history stored locally in SQLite.
- GitHub pull request input and review comments.
- Side-by-side diff suggestions with explicit user approval.
- Authentication and hosted deployment with quotas and abuse protection.
- Multiple provider adapters and a local model option.
- Automated evaluation against a curated, non-sensitive fixture set.

## Assumptions

- The first release is local-only and intended for one user at a time.
- “Small source file” will have a documented maximum size chosen during
  implementation; the exact value remains unresolved.
- The initial per-file input limit is 50 KB and should remain configurable.
- A real AI provider will not be selected or called until the AI integration
  milestone, after reviewing provider cost and data-use terms.
- Static analysis is a separate concept from AI review and may be deferred.

## Success criteria

The first version is successful when a beginner can run it locally, submit a small
source file without executing it, and understand a structured review response;
validation and provider errors are understandable; secrets remain server-side; and
focused tests cover the main request, response, and safety boundaries.

## Unresolved decisions

1. Which AI provider should be supported at the AI integration milestone?
2. What API cost limits and provider data-use terms are acceptable?
3. Should any additional static-analysis tools belong in the first release after the
   basic application works?
