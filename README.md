# Autonomous Code Review Agent

A portfolio project demonstrating how to build a full-stack code-review assistant.
A user pastes or uploads a small Python file, submits it for review, and receives
structured findings about possible bugs and security issues.

## What is implemented

The first milestone is complete and running:

- **React + TypeScript + Vite frontend** — paste Python source or upload a `.py`
  file, submit, and see structured findings with severity badges, line numbers,
  explanations, and suggested fixes.
- **FastAPI backend** — validates every request on the server side, enforces the
  50 KB limit, and returns a stable JSON response.
- **Deterministic static checker** — nine token-based checks covering `eval`,
  `exec`, `os.system`, `subprocess.run`, `subprocess.Popen`, `pickle.load`,
  `pickle.loads`, bare `except:` clauses, and mutable list/dict default arguments.
- **Structured review findings** — each finding carries severity, title,
  explanation, 1-based line numbers, a suggested fix, and a confidence score.
- **Clear mock/demo labelling** — the UI prominently states that findings come from
  deterministic local rules, not from an AI model.
- **34 backend tests** — covering schemas, review service, static checks,
  HTTP endpoints, and error paths.

The submitted code is analyzed as text only. It is never executed, compiled,
imported, passed to a shell, or stored.

## Example review output

Submit this code:

```python
def calculate(expression):
    return eval(expression)
```

The application returns a finding like:

| Field | Value |
|---|---|
| Severity | **high** |
| Title | Dynamic evaluation with eval |
| Line | 2 |
| Explanation | Use of eval(...) can execute input as Python code. |
| Suggested fix | Avoid eval; parse input as data or use an explicit allowlist. |
| Confidence | 98% |

## What the static checker detects

| Pattern | Severity |
|---|---|
| `eval(...)` | high |
| `exec(...)` | high |
| `os.system(...)` | high |
| `pickle.load(...)` / `pickle.loads(...)` | high |
| `subprocess.run(...)` | medium |
| `subprocess.Popen(...)` | medium |
| Mutable list or dict default argument | medium |
| Bare `except:` clause | low |

The checker uses Python's `tokenize` module to inspect source tokens. It will not
catch aliased imports (`import subprocess as sp`) and it is not a security guarantee.
Findings are clearly labelled as deterministic heuristics.

## Local setup

You need **Node.js 18+** and **Python 3.12+**.

### Start the backend

```text
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. The health endpoint is
`GET /health`.

### Start the frontend

Open a second terminal:

```text
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Run the backend tests

```text
cd backend
python -m pytest tests/ -v
```

## Architecture

```text
Browser (React + TypeScript + Vite)
   |
   | POST /api/reviews  (JSON)
   v
FastAPI route  ->  input validation (Pydantic)
   |
   v
ReviewService  ->  MockReviewProvider
                      |
                      v
                  analyze_source()  -- tokenize-based static checks
                      |
                      v
                  list[ReviewFinding]
   |
   v
Validated JSON response  ->  Browser renders findings
```

A replaceable `ReviewProvider` protocol keeps the static checker and any future AI
adapter behind a common interface. No code path executes, imports, or compiles
submitted source.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, plain CSS |
| Backend | Python 3.12+, FastAPI, Pydantic, Uvicorn |
| Static analysis | Python `tokenize` (stdlib only) |
| Tests | pytest |
| Version control | Git, GitHub |

## Safety notes

- Submitted source code is never executed, imported, compiled, or shelled out.
- The 50 KB source limit is enforced on the backend and is configurable.
- No submitted code or review results are stored after the request.
- API keys and backend configuration stay server-side and out of version control.
- Findings are labelled as deterministic heuristics, not guarantees.
- The frontend never renders untrusted HTML from findings.

## Documentation

- [Requirements](docs/REQUIREMENTS.md) — what the project must and must not do.
- [Architecture](docs/ARCHITECTURE.md) — component structure, data flow, and security
  boundaries.
- [Plan](docs/PLAN.md) — milestone history and remaining work.
- [Working instructions](AGENTS.md) — durable rules for future contributors and
  coding agents.

## Limitations and future work

- The checker does not catch aliased imports or every expression form.
- Findings are heuristics; they do not prove code is safe or bug-free.
- No AI provider is integrated yet; a local Ollama model is the planned next step.
- No hosted deployment, authentication, or persistent storage in this version.
- Additional static-analysis tools are deferred until the AI provider milestone.
