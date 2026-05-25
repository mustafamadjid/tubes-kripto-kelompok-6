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


def fake_request(path: str = "/", session: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(url=SimpleNamespace(path=path), session=session or {})


def test_base_shell_uses_secure_vote_brand_and_voter_login_navigation():
    html = render("login.html", {"request": fake_request("/login"), "title": "Login", "error": None})

    assert "SecureVote RSA" in html
    assert "Your Website" not in html
    assert "About us" not in html
    assert "Voter Login" in html
    assert "Ballot" not in html
    assert 'href="/admin/dashboard"' not in html
    assert 'href="/admin/results"' not in html
    assert 'href="/admin/audit-logs"' not in html
    assert 'href="/admin/benchmarks"' not in html


def test_base_shell_shows_only_ballot_for_authenticated_voter():
    html = render(
        "vote.html",
        {
            "request": fake_request("/vote", {"nim": "122140191"}),
            "voter": FakeVoter("Demo Voter"),
            "candidates": [FakeCandidate(1, "Candidate A", "Vision A")],
            "error": None,
        },
    )

    assert "Ballot" in html
    assert "Voter Login" not in html
    assert 'href="/admin/dashboard"' not in html
    assert 'href="/admin/results"' not in html
    assert 'href="/admin/audit-logs"' not in html
    assert 'href="/admin/benchmarks"' not in html


def test_base_shell_shows_admin_menu_only_for_authenticated_admin():
    html = render(
        "admin_dashboard.html",
        {
            "request": fake_request("/admin/dashboard", {"is_admin": True}),
            "total_voters": 10,
            "total_candidates": 3,
            "total_votes": 7,
            "total_audit_logs": 2,
        },
    )

    assert "Dashboard" in html
    assert "Results" in html
    assert "Audit" in html
    assert "Benchmarks" in html
    assert "Voter Login" not in html
    assert "Ballot" not in html


def test_login_page_presents_centered_voter_login_form():
    html = render("login.html", {"request": fake_request("/login"), "title": "Login", "error": None})

    assert "auth-layout-centered" in html
    assert "Masuk sebagai pemilih" in html
    assert 'name="nim"' in html
    assert 'name="password"' in html
    assert "Masuk ke ballot" in html


def test_vote_page_has_accessible_candidate_cards_and_finality_notice():
    html = render(
        "vote.html",
        {
            "request": fake_request("/vote", {"nim": "122140191"}),
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

    results_html = render("recap_result.html", {"request": fake_request("/admin/results", {"is_admin": True}), "result": result})
    audit_html = render(
        "audit_logs.html",
        {
                    "request": fake_request("/admin/audit-logs", {"is_admin": True}),
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
                    "request": fake_request("/admin/benchmarks", {"is_admin": True}),
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
