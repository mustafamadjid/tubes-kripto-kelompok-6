from collections import Counter

from app.domain.enums import AuditEventType, VerificationStatus
from app.domain.exceptions import MalformedVotePlaintextError
from app.domain.plaintext import parse_vote_plaintext
from app.schemas.results import CandidateVoteResult, InvalidVoteDetail, RecapitulationResult


class RecapitulationService:
    def __init__(self, vote_repository, candidate_repository, audit_log_repository, crypto_service) -> None:
        self.vote_repository = vote_repository
        self.candidate_repository = candidate_repository
        self.audit_log_repository = audit_log_repository
        self.crypto_service = crypto_service

    def recapitulate_votes(self) -> RecapitulationResult:
        votes = self.vote_repository.find_all_votes()
        candidates = {candidate.id: candidate for candidate in self.candidate_repository.find_all()}
        counts: Counter[int] = Counter()
        invalid_details: list[InvalidVoteDetail] = []

        self.audit_log_repository.create_log(
            AuditEventType.RECAPITULATION_STARTED.value,
            "vote_record",
            None,
            "Recapitulation started",
        )

        for vote in votes:
            invalid_detail = self._validate_and_count_vote(vote, candidates, counts)
            if invalid_detail is not None:
                invalid_details.append(invalid_detail)

        candidate_results = [
            CandidateVoteResult(candidate_id=cid, candidate_name=candidate.name, vote_count=counts[cid])
            for cid, candidate in sorted(candidates.items())
        ]

        self.audit_log_repository.create_log(
            AuditEventType.RECAPITULATION_COMPLETED.value,
            "vote_record",
            None,
            f"Recapitulation completed: {sum(counts.values())} valid votes",
        )
        return RecapitulationResult(
            total_votes=len(votes),
            valid_votes=sum(counts.values()),
            invalid_votes=len(invalid_details),
            candidate_results=candidate_results,
            invalid_vote_details=invalid_details,
        )

    def _validate_and_count_vote(self, vote, candidates, counts) -> InvalidVoteDetail | None:
        if not self.crypto_service.verify_signature(vote.ciphertext_hash, vote.signature):
            return self._mark_invalid(
                vote,
                VerificationStatus.INVALID_SIGNATURE,
                AuditEventType.INVALID_SIGNATURE_DETECTED.value,
                "Invalid RSA-PSS signature",
            )

        if not self.crypto_service.verify_ciphertext_hash(vote.ciphertext, vote.ciphertext_hash):
            return self._mark_invalid(
                vote,
                VerificationStatus.HASH_MISMATCH,
                AuditEventType.HASH_MISMATCH_DETECTED.value,
                "Ciphertext hash does not match stored hash",
            )

        try:
            plaintext = self.crypto_service.decrypt_vote_ciphertext(vote.ciphertext)
        except Exception:
            return self._mark_invalid(
                vote,
                VerificationStatus.DECRYPTION_FAILED,
                AuditEventType.DECRYPTION_FAILED.value,
                "RSA-OAEP decryption failed",
            )

        try:
            parsed = parse_vote_plaintext(plaintext)
        except MalformedVotePlaintextError:
            return self._mark_invalid(
                vote,
                VerificationStatus.MALFORMED_PLAINTEXT,
                AuditEventType.MALFORMED_PLAINTEXT.value,
                "Vote plaintext is malformed",
            )

        if parsed.candidate_id not in candidates:
            return self._mark_invalid(
                vote,
                VerificationStatus.MALFORMED_PLAINTEXT,
                AuditEventType.MALFORMED_PLAINTEXT.value,
                "Vote references unknown candidate",
            )

        self.vote_repository.update_verification_status(vote.id, VerificationStatus.VALID)
        counts[parsed.candidate_id] += 1
        return None

    def _mark_invalid(self, vote, status: VerificationStatus, event_type: str, reason: str) -> InvalidVoteDetail:
        self.vote_repository.update_verification_status(vote.id, status, reason)
        self.audit_log_repository.create_log(event_type, "vote_record", str(vote.id), reason)
        return InvalidVoteDetail(vote_id=str(vote.id), voter_id=vote.voter_id, status=status.value, reason=reason)
