from datetime import datetime, timezone

from app.domain.enums import AuditEventType
from app.domain.exceptions import CandidateNotFoundError, VoterAlreadyVotedError, VoterNotFoundError
from app.domain.plaintext import build_vote_plaintext
from app.schemas.results import VoteCastResult


class VotingService:
    def __init__(
        self,
        voter_repository,
        candidate_repository,
        vote_repository,
        audit_log_repository,
        crypto_service,
    ) -> None:
        self.voter_repository = voter_repository
        self.candidate_repository = candidate_repository
        self.vote_repository = vote_repository
        self.audit_log_repository = audit_log_repository
        self.crypto_service = crypto_service

    def cast_vote(self, voter_id: str, candidate_id: int) -> VoteCastResult:
        voter = self.voter_repository.find_by_voter_id(voter_id)
        if voter is None:
            raise VoterNotFoundError(f"Voter {voter_id} not found")
        if voter.has_voted:
            self.audit_log_repository.create_log(
                AuditEventType.DOUBLE_VOTE_ATTEMPT.value,
                "voter",
                voter_id,
                "Double vote attempt rejected",
            )
            raise VoterAlreadyVotedError(f"Voter {voter_id} already voted")

        candidate = self.candidate_repository.find_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate {candidate_id} not found")

        timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        plaintext = build_vote_plaintext(voter_id, candidate_id, timestamp)
        ciphertext = self.crypto_service.encrypt_vote_plaintext(plaintext)
        ciphertext_hash = self.crypto_service.hash_ciphertext(ciphertext)
        signature = self.crypto_service.sign_hash(ciphertext_hash)
        vote = self.vote_repository.create_vote_record(voter_id, ciphertext, ciphertext_hash, signature)
        self.voter_repository.mark_as_voted(voter_id)
        self.audit_log_repository.create_log(
            AuditEventType.VOTE_CAST.value,
            "vote_record",
            str(vote.id),
            f"Vote cast for voter {voter_id}",
        )
        return VoteCastResult(voter_id=voter_id, candidate_id=candidate_id, vote_record_id=str(vote.id))
