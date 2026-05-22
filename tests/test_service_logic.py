from dataclasses import dataclass, field

import pytest

from app.domain.enums import VerificationStatus
from app.domain.exceptions import CandidateNotFoundError, VoterAlreadyVotedError, VoterNotFoundError
from app.domain.plaintext import build_vote_plaintext
from app.services.recapitulation_service import RecapitulationService
from app.services.voting_service import VotingService


@dataclass
class FakeVoter:
    voter_id: str
    full_name: str = "Demo Voter"
    has_voted: bool = False


@dataclass
class FakeCandidate:
    id: int
    name: str


@dataclass
class FakeVote:
    id: str
    voter_id: str
    ciphertext: bytes
    ciphertext_hash: str
    signature: bytes
    verification_status: str = VerificationStatus.PENDING.value
    manipulation_reason: str | None = None


class FakeVoterRepository:
    def __init__(self, voters):
        self.voters = voters

    def find_by_voter_id(self, voter_id):
        return self.voters.get(voter_id)

    def mark_as_voted(self, voter_id):
        self.voters[voter_id].has_voted = True


class FakeCandidateRepository:
    def __init__(self, candidates):
        self.candidates = candidates

    def find_by_id(self, candidate_id):
        return self.candidates.get(candidate_id)

    def find_all(self):
        return list(self.candidates.values())


class FakeVoteRepository:
    def __init__(self, votes=None):
        self.votes = votes or []

    def create_vote_record(self, voter_id, ciphertext, ciphertext_hash, signature):
        vote = FakeVote("vote-1", voter_id, ciphertext, ciphertext_hash, signature)
        self.votes.append(vote)
        return vote

    def find_all_votes(self):
        return self.votes

    def update_verification_status(self, vote_id, status, reason=None):
        for vote in self.votes:
            if vote.id == vote_id:
                vote.verification_status = status.value if hasattr(status, "value") else status
                vote.manipulation_reason = reason


class FakeAuditLogRepository:
    def __init__(self):
        self.logs = []

    def create_log(self, event_type, entity_type, entity_id, message):
        self.logs.append((event_type, entity_type, entity_id, message))


class FakeCrypto:
    def __init__(self):
        self.calls = []

    def encrypt_vote_plaintext(self, plaintext):
        self.calls.append("encrypt")
        return plaintext.encode()

    def hash_ciphertext(self, ciphertext):
        self.calls.append("hash")
        return "a" * 64

    def sign_hash(self, hash_hex):
        self.calls.append("sign")
        return b"signature"

    def verify_signature(self, hash_hex, signature):
        return signature == b"signature"

    def verify_ciphertext_hash(self, ciphertext, expected_hash_hex):
        return expected_hash_hex == "a" * 64

    def decrypt_vote_ciphertext(self, ciphertext):
        return ciphertext.decode()


def test_voting_service_rejects_unknown_voter():
    service = VotingService(
        voter_repository=FakeVoterRepository({}),
        candidate_repository=FakeCandidateRepository({1: FakeCandidate(1, "A")}),
        vote_repository=FakeVoteRepository(),
        audit_log_repository=FakeAuditLogRepository(),
        crypto_service=FakeCrypto(),
    )

    with pytest.raises(VoterNotFoundError):
        service.cast_vote("missing", 1)


def test_voting_service_rejects_already_voted_voter():
    service = VotingService(
        voter_repository=FakeVoterRepository({"VOTER001": FakeVoter("VOTER001", has_voted=True)}),
        candidate_repository=FakeCandidateRepository({1: FakeCandidate(1, "A")}),
        vote_repository=FakeVoteRepository(),
        audit_log_repository=FakeAuditLogRepository(),
        crypto_service=FakeCrypto(),
    )

    with pytest.raises(VoterAlreadyVotedError):
        service.cast_vote("VOTER001", 1)


def test_voting_service_rejects_unknown_candidate():
    service = VotingService(
        voter_repository=FakeVoterRepository({"VOTER001": FakeVoter("VOTER001")}),
        candidate_repository=FakeCandidateRepository({}),
        vote_repository=FakeVoteRepository(),
        audit_log_repository=FakeAuditLogRepository(),
        crypto_service=FakeCrypto(),
    )

    with pytest.raises(CandidateNotFoundError):
        service.cast_vote("VOTER001", 99)


def test_voting_service_uses_crypto_pipeline_in_required_order():
    crypto = FakeCrypto()
    voter_repo = FakeVoterRepository({"VOTER001": FakeVoter("VOTER001")})
    vote_repo = FakeVoteRepository()
    service = VotingService(
        voter_repository=voter_repo,
        candidate_repository=FakeCandidateRepository({1: FakeCandidate(1, "A")}),
        vote_repository=vote_repo,
        audit_log_repository=FakeAuditLogRepository(),
        crypto_service=crypto,
    )

    result = service.cast_vote("VOTER001", 1)

    assert result.voter_id == "VOTER001"
    assert crypto.calls == ["encrypt", "hash", "sign"]
    assert voter_repo.voters["VOTER001"].has_voted is True
    assert len(vote_repo.votes) == 1


def test_recapitulation_skips_invalid_signature():
    vote = FakeVote("vote-1", "VOTER001", b"cipher", "a" * 64, b"bad")
    vote_repo = FakeVoteRepository([vote])
    audit_repo = FakeAuditLogRepository()
    service = RecapitulationService(
        vote_repository=vote_repo,
        candidate_repository=FakeCandidateRepository({1: FakeCandidate(1, "A")}),
        audit_log_repository=audit_repo,
        crypto_service=FakeCrypto(),
    )

    result = service.recapitulate_votes()

    assert result.valid_votes == 0
    assert result.invalid_votes == 1
    assert vote.verification_status == VerificationStatus.INVALID_SIGNATURE.value
    assert any(log[0] == "INVALID_SIGNATURE_DETECTED" for log in audit_repo.logs)


def test_recapitulation_counts_valid_votes():
    plaintext = build_vote_plaintext("VOTER001", 1, "2026-05-22T14:30:00+07:00")
    vote = FakeVote("vote-1", "VOTER001", plaintext.encode(), "a" * 64, b"signature")
    service = RecapitulationService(
        vote_repository=FakeVoteRepository([vote]),
        candidate_repository=FakeCandidateRepository({1: FakeCandidate(1, "Candidate A")}),
        audit_log_repository=FakeAuditLogRepository(),
        crypto_service=FakeCrypto(),
    )

    result = service.recapitulate_votes()

    assert result.valid_votes == 1
    assert result.invalid_votes == 0
    assert result.candidate_results[0].candidate_id == 1
    assert result.candidate_results[0].vote_count == 1
