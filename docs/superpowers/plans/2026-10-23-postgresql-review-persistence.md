# PostgreSQL Review Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a privacy-conscious PostgreSQL persistence milestone that stores structured review findings and request metadata without storing submitted Python source code.

**Architecture:** Keep the existing `POST /api/reviews` response unchanged. After a review is successfully produced and validated, persist one review row and zero or more normalized finding rows in a single transaction; a persistence failure returns HTTP 503. Keep persistence behind a repository/service boundary so route and review-service unit tests use fakes, while a focused PostgreSQL integration test verifies the real schema and transaction behavior. Provide explicit internal CLI commands for deleting one review or purging expired reviews; do not add history HTTP endpoints, authentication, or a UI in this milestone.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2.x ORM, Alembic, PostgreSQL 16, psycopg 3, pytest, HTTPX, Docker Compose.

**Spec:** This document’s “Confirmed specification” section, together with [docs/REQUIREMENTS.md](../../REQUIREMENTS.md) and [docs/ARCHITECTURE.md](../../ARCHITECTURE.md). This milestone supersedes only the current documents’ “no database” and “SQLite future idea” statements; all existing source-safety, mock-mode, frontend, and API-contract requirements remain in force.

## Global Constraints

- Never store submitted source code or any reversible representation of it.
- Never execute, compile, import, evaluate, or shell out with submitted source.
- Keep the existing `POST /api/reviews` response shape unchanged.
- Persist only after the review response has been validated.
- A database write failure fails the request with HTTP 503 and a generic user-safe message.
- Do not log submitted source, credentials, or full provider output by default.
- Store timezone-aware UTC timestamps.
- Use PostgreSQL 16 for local Docker development.
- Read the connection string from `DATABASE_URL`; local credentials belong in an untracked `.env`.
- Use `REVIEW_RETENTION_DAYS`, default `30`, accepting only positive integers up to `365`.
- Do not add user accounts, authentication, authorization, history endpoints, frontend history UI, hosted deployment, or automatic GitHub reviews.
- Reviews with zero findings are persisted with zero related finding rows.

## Confirmed specification

### Scope and deployment

- PostgreSQL is a new milestone after the existing stateless first milestone.
- Local development must work with Docker Compose and PostgreSQL 16.
- A fresh database is sufficient; no historical migration/import is required.
- Retention purge is invoked by an external scheduler or cron job documented for Docker Compose/host use.

### Stored data

Each `reviews` row contains:

- `id`: backend-generated UUID primary key.
- `filename`: request display metadata.
- `language`: currently `python`.
- `mode`: current review mode, such as `mock`.
- `created_at`: timezone-aware UTC timestamp.
- `expires_at`: timezone-aware UTC timestamp calculated at write time.
- `finding_count`: count of related findings.

Each related `findings` row contains the existing structured finding fields: severity, title, explanation, optional `line_start`, optional `line_end`, optional `suggested_fix`, and optional confidence. It references its parent review with a foreign key and is deleted with that review. No source text is stored in either table.

### Runtime behavior

- `POST /api/reviews` continues returning language, mode, and findings exactly as before.
- The route/service persists the review and all findings in one atomic transaction.
- Any persistence failure rolls back the review and findings and returns HTTP 503.
- There are no read/list/retrieval HTTP endpoints in this milestone.
- Internal deletion is available only through:
  - `python -m app retention delete <uuid>`
  - `python -m app retention purge-expired`
- The delete command reports success/failure without exposing source or unnecessary identifiers.
- The purge command prints the number of deleted reviews and exits non-zero on database failure.
- Automatic retention deletion removes rows whose `expires_at` is at or before the current UTC time.

## File Map

- Create `backend/app/database.py`: `DATABASE_URL` loading, SQLAlchemy engine/session factory, and transaction-scoped session dependency.
- Create `backend/app/models.py`: SQLAlchemy `ReviewModel` and `FindingModel` tables and relationships.
- Create `backend/app/persistence.py`: typed persistence boundary and implementation for atomic review writes and retention/delete operations.
- Create `backend/app/config.py`: validated `REVIEW_RETENTION_DAYS` configuration with default 30 and maximum 365.
- Create `backend/app/retention.py`: CLI parser and delete/purge command orchestration.
- Create `backend/alembic.ini`, `backend/alembic/env.py`, and `backend/alembic/versions/0001_create_review_tables.py`: versioned schema setup.
- Create `backend/docker-compose.yml` or extend the repository’s chosen Compose file: PostgreSQL 16 service and backend connection wiring.
- Modify `backend/requirements.txt`: SQLAlchemy, Alembic, psycopg, and test-only PostgreSQL support as needed.
- Modify `backend/app/main.py` and/or the existing review route/service: inject persistence and map persistence failures to HTTP 503 without changing successful response data.
- Modify `backend/README.md` and root [README.md](../../README.md): local database setup, migration, CLI, retention scheduling, and privacy rules.
- Modify [docs/REQUIREMENTS.md](../../REQUIREMENTS.md), [docs/ARCHITECTURE.md](../../ARCHITECTURE.md), and [docs/PLAN.md](../../PLAN.md): mark persistence as this new milestone while preserving first-milestone non-goals.
- Create `backend/tests/test_persistence.py`: repository unit tests using an in-memory/fake session boundary.
- Create `backend/tests/test_database_integration.py`: focused PostgreSQL smoke/transaction tests, skipped with a clear reason when the configured test database is unavailable.
- Modify `backend/tests/test_reviews.py` and service tests: verify persistence is called and failures become HTTP 503 while response shape remains stable.
- Create `backend/tests/test_retention.py`: configuration and CLI behavior tests.

## Review Focus

- **Source leakage:** database rows, exception messages, and logs must not contain submitted source; test persisted objects and failure paths with a unique source marker.
- **Partial transactions:** a failure while inserting a finding must leave no review or finding rows; test rollback against PostgreSQL.
- **Retention boundaries:** exactly-expired rows are purged, future rows remain, and UTC/timezone handling is stable.
- **Configuration abuse:** zero, negative, non-integer, and over-365 retention values fail clearly; missing value uses 30.
- **Operational safety:** deleting one UUID cannot trigger broad deletion, and purge reports a count with a non-zero exit on database failure.

---

### Task 1: Add validated database configuration and dependencies

**Files:**
- Create: `backend/app/config.py`
- Modify: `backend/requirements.txt`
- Modify: `backend/tests/test_retention.py`

**Interfaces:**
- Produces `get_retention_days(environ: Mapping[str, str] | None = None) -> int`.
- Produces `database_url(environ: Mapping[str, str] | None = None) -> str`.

- [ ] **Step 1: Write failing tests** for missing `REVIEW_RETENTION_DAYS` returning `30`, valid `1` and `365`, and invalid `0`, `-1`, `366`, and non-integer values raising a clear configuration error. Test that missing `DATABASE_URL` is rejected when database functionality is initialized.
- [ ] **Step 2: Run `python -m pytest backend/tests/test_retention.py -v` and verify the new tests fail because configuration helpers do not exist.
- [ ] **Step 3: Implement the configuration helpers and add SQLAlchemy 2.x, Alembic, and psycopg 3 dependencies with compatible version bounds.
- [ ] **Step 4: Run the focused tests and verify they pass.
- [ ] **Step 5: Commit with `feat: add database configuration` including the test and dependency manifest changes.

### Task 2: Define ORM models and Alembic migration

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/database.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/0001_create_review_tables.py`
- Create: `backend/tests/test_models.py`

**Interfaces:**
- Produces `ReviewModel` and `FindingModel`.
- Produces `create_session_factory(database_url: str) -> sessionmaker`.
- `FindingModel.review_id` references `ReviewModel.id` with cascade delete.

- [ ] **Step 1: Write failing model tests** asserting the review columns, finding columns, UUID primary key, UTC-aware timestamps, foreign key, cascade relationship, and zero-finding review shape.
- [ ] **Step 2: Run `python -m pytest backend/tests/test_models.py -v` and verify failure before the models exist.
- [ ] **Step 3: Implement SQLAlchemy models with no source-code column and configure Alembic metadata.
- [ ] **Step 4: Generate/write the explicit initial Alembic migration for PostgreSQL 16, including indexes needed for `expires_at` purge and review lookup by UUID.
- [ ] **Step 5: Run model tests and an offline Alembic validation; verify the migration contains only the two intended tables and constraints.
- [ ] **Step 6: Commit with `feat: define review persistence schema`.

### Task 3: Implement the atomic persistence repository

**Files:**
- Create: `backend/app/persistence.py`
- Create: `backend/tests/test_persistence.py`

**Interfaces:**
- Consumes the existing validated `ReviewResponse` and request metadata.
- Produces `ReviewRepository.save_review(request: ReviewRequest, response: ReviewResponse, created_at: datetime | None = None) -> UUID`.
- Produces `ReviewRepository.delete_review(review_id: UUID) -> bool`.
- Produces `ReviewRepository.purge_expired(now: datetime | None = None) -> int`.

- [ ] **Step 1: Write failing repository tests** for metadata/finding mapping, zero findings, UUID generation, calculated expiry, no source persistence, single-transaction success, rollback on child insert failure, exact-ID deletion, and expired-only purge.
- [ ] **Step 2: Run `python -m pytest backend/tests/test_persistence.py -v` and verify failure before the repository exists.
- [ ] **Step 3: Implement `ReviewRepository` using one transaction for the review row and all finding rows; set `finding_count` from the validated response and use UTC-aware timestamps.
- [ ] **Step 4: Ensure repository exceptions preserve rollback and are converted to a typed persistence error without including source text.
- [ ] **Step 5: Run the repository tests and verify they pass with a fake/in-memory session boundary.
- [ ] **Step 6: Commit with `feat: persist structured review findings`.

### Task 4: Integrate persistence into the review request

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/review_service.py` or the existing route integration point
- Modify: `backend/tests/test_reviews.py`
- Modify: `backend/tests/test_review_service.py`

**Interfaces:**
- Existing successful `POST /api/reviews` response remains `ReviewResponse`.
- Persistence is injected as a repository dependency rather than constructed inside the provider.

- [ ] **Step 1: Write failing route tests** asserting that a successful review calls persistence, returns the unchanged response body, and a persistence failure returns HTTP 503 with a generic message.
- [ ] **Step 2: Run the focused route/service tests and verify failure before integration exists.
- [ ] **Step 3: Inject the repository after response validation and before returning success; map only persistence failures to 503 and preserve existing validation/provider error behavior.
- [ ] **Step 4: Add an assertion that a unique source marker is absent from repository error logs/messages and persisted arguments.
- [ ] **Step 5: Run the backend review tests and verify all pass.
- [ ] **Step 6: Commit with `feat: require persistence for review success`.

### Task 5: Add retention and deletion CLI operations

**Files:**
- Create: `backend/app/retention.py`
- Create: `backend/tests/test_retention.py`

**Interfaces:**
- CLI command: `python -m app retention delete <uuid>`.
- CLI command: `python -m app retention purge-expired`.
- `delete` reports whether one matching review was deleted and exits non-zero on invalid UUID or database failure.
- `purge-expired` prints `Deleted <count> expired reviews.` and exits non-zero on database failure.

- [ ] **Step 1: Write failing CLI tests** for valid deletion, invalid UUID, no matching UUID, purge count, and repository/database failure exit codes.
- [ ] **Step 2: Run `python -m pytest backend/tests/test_retention.py -v` and verify the CLI tests fail before the command exists.
- [ ] **Step 3: Implement the explicit subcommands, using the repository’s exact-ID delete and UTC expiry purge operations; do not expose an HTTP route.
- [ ] **Step 4: Run CLI tests and verify output does not include source text or unnecessary review data.
- [ ] **Step 5: Commit with `feat: add review retention commands`.

### Task 6: Add PostgreSQL 16 Compose and integration verification

**Files:**
- Create or modify: `backend/docker-compose.yml` (or the repository’s selected Compose file)
- Create: `backend/tests/test_database_integration.py`
- Modify: `backend/README.md`

**Interfaces:**
- Compose provides PostgreSQL 16 with a local-only development database and an untracked `.env`-driven `DATABASE_URL`.
- Integration tests use a dedicated test database and never use production/local review data.

- [ ] **Step 1: Write the PostgreSQL integration tests** for migration application, review-plus-findings persistence, zero findings, cascade deletion, exact expiry purge, and rollback after a forced finding insert failure.
- [ ] **Step 2: Start PostgreSQL 16 with Docker Compose, apply Alembic migrations, and run `python -m pytest backend/tests/test_database_integration.py -v`; verify tests fail until the schema/repository wiring is complete.
- [ ] **Step 3: Add Compose health checks, environment-variable wiring, and a documented untracked `.env.example` containing placeholders only.
- [ ] **Step 4: Run the integration tests and verify they pass; stop the test database after verification.
- [ ] **Step 5: Commit with `test: verify PostgreSQL persistence integration`.

### Task 7: Document the milestone and retention scheduling

**Files:**
- Modify: `backend/README.md`
- Modify: `README.md`
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/PLAN.md`

**Interfaces:**
- Documentation must distinguish the completed stateless first milestone from this PostgreSQL persistence milestone.
- Documentation must include migration, local Compose startup, CLI deletion/purge commands, `REVIEW_RETENTION_DAYS`, and an external cron/scheduler example.

- [ ] **Step 1: Update requirements to move database persistence from “non-goal” to this explicitly scoped follow-on milestone, while retaining “never store submitted source” and deferring auth/history UI.
- [ ] **Step 2: Update architecture with the repository boundary, transaction boundary, HTTP 503 behavior, schema summary, and CLI-only deletion surface.
- [ ] **Step 3: Update README and backend README with commands such as `docker compose up -d`, `alembic upgrade head`, `python -m app retention purge-expired`, and the required environment configuration.
- [ ] **Step 4: Update PLAN.md with the milestone status and its remaining authentication/history work.
- [ ] **Step 5: Review documentation for contradictions with the confirmed specification and commit with `docs: specify PostgreSQL persistence milestone`.

### Task 8: Run the complete verification gate

**Files:**
- No new files; verify all changed backend and documentation files.

- [ ] **Step 1: Run unit and route tests: `python -m pytest backend/tests -v`.
- [ ] **Step 2: Run the PostgreSQL integration smoke test against PostgreSQL 16.
- [ ] **Step 3: Run Alembic migration upgrade from a fresh database and confirm the two expected tables and cascade constraint.
- [ ] **Step 4: Exercise a review containing a unique source marker and verify the marker is absent from database rows, CLI output, and logs.
- [ ] **Step 5: Confirm the frontend build and existing frontend tests remain unchanged and passing.
- [ ] **Step 6: Commit with `test: verify PostgreSQL review persistence milestone`.

## Deferred after this milestone

Authentication and authorization, review-history HTTP endpoints, frontend history UI, hosted deployment, per-user retention, source-code storage, source retrieval, multi-user quotas, and automatic in-process scheduling remain deferred until separately specified.
