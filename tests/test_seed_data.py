import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from types import SimpleNamespace

from scripts.seed_data import apply_demo_voter_status, demo_nim, demo_voter_has_voted


def test_demo_double_vote_account_is_seeded_as_already_voted():
    assert demo_nim(99) == "122140099"
    assert demo_voter_has_voted(99) is True


def test_regular_demo_voters_are_seeded_as_not_voted():
    assert demo_voter_has_voted(1) is False
    assert demo_voter_has_voted(2) is False
    assert demo_voter_has_voted(3) is False


def test_existing_double_vote_account_is_marked_as_already_voted():
    voter = SimpleNamespace(nim="122140099", has_voted=False)

    apply_demo_voter_status(voter)

    assert voter.has_voted is True
