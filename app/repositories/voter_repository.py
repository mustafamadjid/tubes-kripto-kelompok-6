from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.voter import Voter


class VoterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_nim(self, nim: str) -> Voter | None:
        return self.db.scalar(select(Voter).where(Voter.nim == nim))

    def mark_as_voted(self, nim: str) -> None:
        voter = self.find_by_nim(nim)
        if voter is not None:
            voter.has_voted = True
            self.db.add(voter)

    def count_all(self) -> int:
        return len(self.db.scalars(select(Voter)).all())
