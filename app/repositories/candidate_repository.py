from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate


class CandidateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, candidate_id: int) -> Candidate | None:
        return self.db.get(Candidate, candidate_id)

    def find_all(self) -> list[Candidate]:
        return list(self.db.scalars(select(Candidate).order_by(Candidate.id)).all())

    def count_all(self) -> int:
        return len(self.find_all())
