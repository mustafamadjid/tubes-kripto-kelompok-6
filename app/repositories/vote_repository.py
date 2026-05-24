from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import VerificationStatus
from app.models.vote_record import VoteRecord


class VoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_vote_record(self, nim: str, ciphertext: bytes, ciphertext_hash: str, signature: bytes) -> VoteRecord:
        vote = VoteRecord(
            nim=nim,
            ciphertext=ciphertext,
            ciphertext_hash=ciphertext_hash,
            signature=signature,
        )
        self.db.add(vote)
        return vote

    def find_all_votes(self) -> list[VoteRecord]:
        return list(self.db.scalars(select(VoteRecord).order_by(VoteRecord.created_at)).all())

    def find_by_id(self, vote_id: str) -> VoteRecord | None:
        return self.db.get(VoteRecord, vote_id)

    def count_all(self) -> int:
        return len(self.find_all_votes())

    def update_verification_status(
        self,
        vote_id: str,
        status: VerificationStatus,
        reason: str | None = None,
    ) -> None:
        vote = self.find_by_id(str(vote_id))
        if vote is not None:
            vote.verification_status = status.value
            vote.manipulation_reason = reason
            self.db.add(vote)
