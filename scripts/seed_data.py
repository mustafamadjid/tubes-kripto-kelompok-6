import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import Candidate, Voter
from app.services.auth_service import hash_password


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
        if not db.query(Voter).count():
            db.add_all(
                [
                    Voter(
                        voter_id=f"VOTER{i:03d}",
                        full_name=f"Mahasiswa {i:03d}",
                        password_hash=hash_password("password123"),
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
