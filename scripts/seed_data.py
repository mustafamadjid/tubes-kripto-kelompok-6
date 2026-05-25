import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import Candidate, VoteRecord, Voter
from app.services.auth_service import hash_password


def demo_nim(index: int) -> str:
    return f"12214{index:04d}"


def demo_voter_has_voted(index: int) -> bool:
    return index == 99


def apply_demo_voter_status(voter: Voter) -> None:
    if voter.nim == demo_nim(99):
        voter.has_voted = True


def normalize_demo_nim(value: str) -> str:
    if value.startswith("VOTER") and value[5:].isdigit():
        return demo_nim(int(value[5:]))
    return value


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Candidate).count():
            db.add_all(
                [
                    Candidate(id=1, name="Kandidat A", description="Fokus pada transparansi dan keamanan data."),
                    Candidate(id=2, name="Kandidat B", description="Fokus pada kemudahan akses mahasiswa."),
                    Candidate(id=3, name="Kandidat C", description="Fokus pada audit dan akuntabilitas."),
                ]
            )
        voters = db.query(Voter).all()
        for voter in voters:
            voter.nim = normalize_demo_nim(voter.nim)
            apply_demo_voter_status(voter)
        for vote_record in db.query(VoteRecord).all():
            vote_record.nim = normalize_demo_nim(vote_record.nim)

        if not voters:
            db.add_all(
                [
                    Voter(
                        nim=demo_nim(i),
                        full_name=f"Mahasiswa {i:03d}",
                        password_hash=hash_password("password123"),
                        has_voted=demo_voter_has_voted(i),
                    )
                    for i in range(1, 501)
                ]
            )
        db.commit()
        print("Seed complete: 500 voters and 3 candidates are available")
    finally:
        db.close()


if __name__ == "__main__":
    main()
