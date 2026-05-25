# Role-Based Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restrict visible navigation so voters only see voter flow links, while admin-only menu items appear only for authenticated admins.

**Architecture:** Keep existing route protections and make the shared base template session-aware. Cover the behavior with template-rendering tests before changing production markup.

**Tech Stack:** FastAPI, Starlette sessions, Jinja2 templates, pytest.

---

### Task 1: Template Tests

**Files:**
- Modify: `tests/test_ui_templates.py`
- Test: `tests/test_ui_templates.py`

- [ ] **Step 1: Write the failing tests**

Add tests that render `base.html` through existing child templates with fake request/session objects. Assert unauthenticated voters see `Voter Login`, authenticated voters see `Ballot`, and authenticated admins see only `Dashboard`, `Results`, `Audit`, and `Benchmarks` from the admin menu set.

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m pytest tests/test_ui_templates.py -q`
Expected: FAIL because the current base template always renders admin and voter menu items together.

### Task 2: Session-Aware Navigation

**Files:**
- Modify: `app/templates/base.html`
- Test: `tests/test_ui_templates.py`

- [ ] **Step 1: Implement minimal template branching**

Use `request.session.get("is_admin")` and `request.session.get("nim")` to decide which menu group to render.

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests/test_ui_templates.py -q`
Expected: PASS.

- [ ] **Step 3: Run broader verification**

Run: `python -m pytest -q`
Expected: PASS.
