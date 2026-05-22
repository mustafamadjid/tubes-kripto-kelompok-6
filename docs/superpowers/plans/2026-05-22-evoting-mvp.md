# E-Voting MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP described in `planning.md`: a FastAPI e-voting prototype using RSA-OAEP, SHA-256, RSA-PSS, PostgreSQL-ready persistence, unit tests, scripts, and server-rendered UI.

**Architecture:** Use a modular monolith with thin routers, service orchestration, repository database access, SQLAlchemy models, and an isolated crypto service. The app remains demo-friendly and avoids production-grade scope outside the planning document.

**Tech Stack:** Python 3.12+, FastAPI, Jinja2, SQLAlchemy 2.x, Alembic, PostgreSQL via psycopg, cryptography, Pytest, Docker Compose.

---

### Task 1: Foundation and Tests

**Files:**
- Create: `requirements.txt`, `.env.example`, `.gitignore`, `docker-compose.yml`, `Dockerfile`
- Create: `app/` package and `tests/` package
- Test: `tests/test_plaintext.py`, `tests/test_crypto_service.py`, `tests/test_service_logic.py`

- [ ] Write failing unit tests for plaintext parsing, crypto behavior, voting service validation, and recapitulation invalid-vote handling.
- [ ] Run targeted tests and verify they fail because implementation is missing.

### Task 2: Domain, Models, Repositories

**Files:**
- Create: `app/domain/`, `app/models/`, `app/repositories/`
- Create: SQLAlchemy models and repository methods needed by services.

- [ ] Implement enums, exceptions, plaintext builder/parser, database session, and models.
- [ ] Implement repositories with small database methods.
- [ ] Run unit tests for pure domain logic.

### Task 3: Services and Scripts

**Files:**
- Create: `app/services/`
- Create: `scripts/generate_keys.py`, `scripts/seed_data.py`, `scripts/manipulate_vote.py`, `scripts/run_benchmark.py`

- [ ] Implement `CryptoService`, `AuthService`, `VotingService`, `RecapitulationService`, `AuditLogService`, and `BenchmarkService`.
- [ ] Implement scripts for key generation, seed data, manipulation demo, and benchmark.
- [ ] Run crypto and service unit tests.

### Task 4: FastAPI Routes and UI

**Files:**
- Create: `app/main.py`, `app/routers/`, `app/templates/`, `app/static/styles.css`

- [ ] Implement voter and admin routes with sessions.
- [ ] Implement Jinja pages using the provided UI reference: light pink surfaces, black typography, student-friendly illustration-like layout, and `#bfa344` as the primary accent.
- [ ] Keep route handlers thin and delegate logic to services.

### Task 5: Documentation and Verification

**Files:**
- Create: `README.md`
- Create: `alembic.ini`, `alembic/`

- [ ] Add setup, migration, key generation, seed, test, benchmark, and demo instructions.
- [ ] Run `pytest`.
- [ ] Run a smoke import of the FastAPI app.
