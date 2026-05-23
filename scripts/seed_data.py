"""Seed script — mendukung dua mode: production dan demo.

Penggunaan:
    python scripts/seed_data.py           # mode dari .env (default: production)
    python scripts/seed_data.py --demo    # paksa mode demo
    python scripts/seed_data.py --prod    # paksa mode production
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import Candidate, Voter
from app.services.auth_service import hash_password
from app.config import settings


CANDIDATES = [
    Candidate(id=1, name="Kandidat A", description="Fokus pada transparansi dan keamanan data."),
    Candidate(id=2, name="Kandidat B", description="Fokus pada kemudahan akses mahasiswa."),
    Candidate(id=3, name="Kandidat C", description="Fokus pada audit dan akuntabilitas."),
]

# ── Voter untuk mode PRODUCTION ───────────────────────────────────────────────
# voter_id = NIM 9 digit (sesuai yang ada di email @student.itera.ac.id)
# Contoh email: muhammad.123140148@student.itera.ac.id → voter_id = "123140148"
PRODUCTION_VOTERS = [
    Voter(voter_id="123140148", full_name="Muhammad Contoh",    password_hash=hash_password("password123")),
    Voter(voter_id="123140149", full_name="Siti Contoh",        password_hash=hash_password("password123")),
    Voter(voter_id="123140150", full_name="Budi Contoh",        password_hash=hash_password("password123")),
    # tambah NIM mahasiswa peserta voting di sini
]

# ── Voter untuk mode DEMO ─────────────────────────────────────────────────────
# voter_id = username Gmail dengan titik diganti underscore
# Contoh email: budi.santoso@gmail.com → voter_id = "budi_santoso"
# Contoh email: namatanpattitik@gmail.com → voter_id = "namatanpattitik"
DEMO_VOTERS = [
    Voter(voter_id="demo_voter1",   full_name="Demo Voter 1",  password_hash=hash_password("password123")),
    Voter(voter_id="demo_voter2",   full_name="Demo Voter 2",  password_hash=hash_password("password123")),
    Voter(voter_id="demo_voter3",   full_name="Demo Voter 3",  password_hash=hash_password("password123")),
    # ↓ Tambahkan entry sesuai akun Gmail peserta demo
    # Voter(voter_id="nama_kamu",   full_name="Nama Kamu",     password_hash=hash_password("password123")),
    # Voter(voter_id="nama_teman",  full_name="Nama Teman",    password_hash=hash_password("password123")),
]


def get_mode() -> str:
    if "--demo" in sys.argv:
        return "demo"
    if "--prod" in sys.argv:
        return "production"
    return settings.oauth_mode  # ambil dari .env


def main() -> None:
    mode = get_mode()
    print(f"[seed] Running in '{mode}' mode")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Candidates — sama untuk semua mode
        if not db.query(Candidate).count():
            db.add_all(CANDIDATES)
            print(f"[seed] Added {len(CANDIDATES)} candidates")
        else:
            print("[seed] Candidates already exist, skipping")

        # Voters — berbeda per mode
        if not db.query(Voter).count():
            voters = DEMO_VOTERS if mode == "demo" else PRODUCTION_VOTERS
            db.add_all(voters)
            db.commit()
            print(f"[seed] Added {len(voters)} voters ({mode} mode)")
            print()
            print("  voter_id yang terdaftar:")
            for v in voters:
                print(f"    {v.voter_id!r:30s} → {v.full_name}")
            print()
            if mode == "demo":
                print("  Pastikan akun Gmail peserta demo formatnya cocok:")
                print("  email: nama.belakang@gmail.com  →  voter_id: nama_belakang")
            else:
                print("  Pastikan NIM di email @student.itera.ac.id cocok dengan voter_id di atas.")
        else:
            print("[seed] Voters already exist, skipping")

        db.commit()
        print("[seed] Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
