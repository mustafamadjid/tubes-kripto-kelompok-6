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

    def create(self, name: str, description: str | None) -> Candidate:
        candidate = Candidate(name=name, description=description)
        self.db.add(candidate)
        return candidate

    def update(self, candidate_id: int, name: str, description: str | None) -> Candidate | None:
        candidate = self.find_by_id(candidate_id)
        if candidate is None:
            return None
        candidate.name = name
        candidate.description = description
        self.db.add(candidate)
        return candidate

    def delete(self, candidate_id: int) -> bool:
        candidate = self.find_by_id(candidate_id)
        if candidate is None:
            return False
        self.db.delete(candidate)
        return True
