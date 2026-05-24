import pytest

from app.domain.exceptions import MalformedVotePlaintextError
from app.domain.plaintext import build_vote_plaintext, parse_vote_plaintext


def test_build_vote_plaintext_uses_required_format():
    plaintext = build_vote_plaintext(
        nim="122140191",
        candidate_id=2,
        timestamp="2026-05-22T14:30:00+07:00",
    )

    assert plaintext == "nim:122140191|candidate_id:2|timestamp:2026-05-22T14:30:00+07:00"


def test_parse_vote_plaintext_returns_structured_data():
    parsed = parse_vote_plaintext(
        "nim:122140191|candidate_id:2|timestamp:2026-05-22T14:30:00+07:00"
    )

    assert parsed.nim == "122140191"
    assert parsed.candidate_id == 2
    assert parsed.timestamp == "2026-05-22T14:30:00+07:00"


@pytest.mark.parametrize(
    "plaintext",
    [
        "candidate_id:2|timestamp:2026-05-22T14:30:00+07:00",
        "nim:122140191|timestamp:2026-05-22T14:30:00+07:00",
        "nim:122140191|candidate_id:2",
        "nim:122140191|candidate_id:abc|timestamp:2026-05-22T14:30:00+07:00",
        "nim:122140191|candidate_id:2|timestamp:not-a-date",
    ],
)
def test_parse_vote_plaintext_rejects_malformed_values(plaintext):
    with pytest.raises(MalformedVotePlaintextError):
        parse_vote_plaintext(plaintext)
