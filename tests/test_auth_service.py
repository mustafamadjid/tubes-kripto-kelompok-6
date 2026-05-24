from dataclasses import dataclass

import pytest

from app.services.auth_service import AuthService, hash_password


@dataclass
class FakeVoter:
    nim: str
    password_hash: str


class FakeVoterRepository:
    def __init__(self) -> None:
        self.voters = {
            "122140191": FakeVoter(
                nim="122140191",
                password_hash=hash_password("password123"),
            )
        }
        self.looked_up_nim = None

    def find_by_nim(self, nim):
        self.looked_up_nim = nim
        return self.voters.get(nim)

    def find_by_voter_id(self, voter_id):
        pytest.fail("authenticate_voter must look up voters by nim, not voter_id")


def test_authenticate_voter_uses_nim_and_password():
    repository = FakeVoterRepository()

    voter = AuthService(repository).authenticate_voter("122140191", "password123")

    assert voter is not None
    assert voter.nim == "122140191"
    assert repository.looked_up_nim == "122140191"


def test_authenticate_voter_rejects_wrong_password_for_nim():
    repository = FakeVoterRepository()

    voter = AuthService(repository).authenticate_voter("122140191", "wrong")

    assert voter is None
