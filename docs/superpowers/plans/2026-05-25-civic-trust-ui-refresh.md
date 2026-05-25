# Civic Trust UI Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Civic Trust Dashboard UI refresh for the FastAPI/Jinja e-voting web app.

**Architecture:** Keep the existing server-rendered architecture. Add template-level regression tests for visible UI contract, then update Jinja templates and the single stylesheet without changing routes, services, or database behavior.

**Tech Stack:** FastAPI, Jinja2 templates, plain CSS, pytest.

---

### Task 1: Add UI Contract Tests

**Files:**
- Create: `tests/test_ui_templates.py`
- Read: `app/templates/*.html`

- [ ] **Step 1: Write failing tests**

Create `tests/test_ui_templates.py` with direct Jinja rendering tests:

```python
from dataclasses import dataclass
from types import SimpleNamespace

from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")


@dataclass
class FakeCandidate:
    id: int
    name: str
    description: str


@dataclass
class FakeVoter:
    full_name: str
    has_voted: bool = False


def render(name: str, context: dict) -> str:
    template = templates.env.get_template(name)
    return template.render(**context)


def test_base_shell_uses_secure_vote_brand_and_app_navigation():
    html = render("login.html", {"request": SimpleNamespace(), "title": "Login", "error": None})

    assert "SecureVote RSA" in html
    assert "Your Website" not in html
    assert "About us" not in html
    assert "Voter Login" in html
    assert "Dashboard" in html
    assert "Audit" in html


def test_login_page_presents_civic_trust_portal_and_crypto_assurance():
    html = render("login.html", {"request": SimpleNamespace(), "title": "Login", "error": None})

    assert "Masuk sebagai pemilih" in html
    assert "Encrypted" in html
    assert "Hashed" in html
    assert "Signed" in html
    assert "Admin Console" in html


def test_vote_page_has_accessible_candidate_cards_and_finality_notice():
    html = render(
        "vote.html",
        {
            "request": SimpleNamespace(),
            "voter": FakeVoter("Demo Voter"),
            "candidates": [FakeCandidate(1, "Candidate A", "Vision A")],
            "error": None,
        },
    )

    assert 'class="candidate-option"' in html
    assert 'class="candidate-radio"' in html
    assert "Pilihan bersifat final" in html
    assert "Kirim suara terenkripsi" in html


def test_results_audit_and_benchmark_tables_are_responsive():
    result = SimpleNamespace(
        total_votes=1,
        valid_votes=1,
        invalid_votes=0,
        candidate_results=[SimpleNamespace(candidate_name="Candidate A", vote_count=1)],
        invalid_vote_details=[],
    )

    results_html = render("recap_result.html", {"request": SimpleNamespace(), "result": result})
    audit_html = render(
        "audit_logs.html",
        {
            "request": SimpleNamespace(),
            "logs": [
                SimpleNamespace(
                    created_at="2026-05-25 10:00",
                    event_type="VOTE_CAST",
                    entity_type="vote",
                    entity_id="vote-1",
                    message="Recorded",
                )
            ],
        },
    )
    benchmark_html = render(
        "benchmark.html",
        {
            "request": SimpleNamespace(),
            "records": [
                SimpleNamespace(
                    operation_name="encrypt",
                    duration_ms=1.2,
                    sample_size=10,
                    created_at="2026-05-25 10:00",
                )
            ],
        },
    )

    assert 'class="table-wrap"' in results_html
    assert 'class="table-wrap"' in audit_html
    assert 'class="table-wrap"' in benchmark_html
    assert "status-chip" in results_html
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_ui_templates.py -v
```

Expected: tests fail because the current templates still use `Your Website`, generic navigation, decorative login copy, old candidate class names, and bare tables.

- [ ] **Step 3: Keep tests staged only after implementation passes**

Do not commit yet. These tests define the UI contract for later tasks.

### Task 2: Refresh Template Structure

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/templates/login.html`
- Modify: `app/templates/admin_login.html`
- Modify: `app/templates/vote.html`
- Modify: `app/templates/vote_success.html`
- Modify: `app/templates/admin_dashboard.html`
- Modify: `app/templates/recap_result.html`
- Modify: `app/templates/audit_logs.html`
- Modify: `app/templates/benchmark.html`

- [ ] **Step 1: Replace base shell**

Update `app/templates/base.html` to use `SecureVote RSA`, app-specific nav labels, and dashboard shell classes.

- [ ] **Step 2: Replace voter login layout**

Update `app/templates/login.html` to use a portal form, crypto assurance panel, and secondary admin console link.

- [ ] **Step 3: Replace admin login and success panels**

Update `app/templates/admin_login.html` and `app/templates/vote_success.html` with the shared panel/card structure.

- [ ] **Step 4: Replace ballot markup**

Update `app/templates/vote.html` with candidate radio cards using `candidate-option` and `candidate-radio`, plus finality notice and encrypted submit copy.

- [ ] **Step 5: Replace admin and data-page markup**

Update dashboard, results, audit logs, and benchmark templates with KPI cards, responsive `table-wrap` containers, status chips, and concise helper text.

- [ ] **Step 6: Run UI contract tests**

Run:

```bash
pytest tests/test_ui_templates.py -v
```

Expected: tests may still fail visually-related class checks until CSS classes are added, but template text and wrappers should now be present.

### Task 3: Replace Stylesheet With Civic Dashboard System

**Files:**
- Modify: `app/static/styles.css`

- [ ] **Step 1: Replace visual tokens and base layout**

Rewrite `styles.css` around civic blue/slate/white/amber tokens, body background, content shell, and responsive containers.

- [ ] **Step 2: Add component styles**

Add styles for header, nav active states, buttons, forms, panels, alert states, KPI cards, candidate cards, chips, table wrappers, dense tables, and code blocks.

- [ ] **Step 3: Add accessibility and responsive rules**

Add visible `:focus-visible` rings, touch-friendly button/input sizing, `prefers-reduced-motion`, mobile grids, and horizontal table scrolling.

- [ ] **Step 4: Run UI contract tests**

Run:

```bash
pytest tests/test_ui_templates.py -v
```

Expected: all new UI contract tests pass.

### Task 4: Full Verification

**Files:**
- Read: all modified templates and CSS

- [ ] **Step 1: Run full test suite**

Run:

```bash
pytest
```

Expected: all tests pass.

- [ ] **Step 2: Inspect changed files**

Run:

```bash
git diff -- app/templates app/static tests/test_ui_templates.py
```

Expected: diff shows only UI/template/test changes aligned with the spec.

- [ ] **Step 3: Report completion**

Summarize changed files, tests run, and any remaining visual verification limitations.
