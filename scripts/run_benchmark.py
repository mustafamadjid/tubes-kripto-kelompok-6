import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.repositories.benchmark_repository import BenchmarkRepository
from app.services.benchmark_service import BenchmarkService
from app.services.factory import create_crypto_service


def main() -> None:
    crypto = create_crypto_service()
    benchmark = BenchmarkService()
    db = SessionLocal()
    repo = BenchmarkRepository(db)
    try:
        plaintext = "voter_id:VOTER001|candidate_id:1|timestamp:2026-05-22T14:30:00+07:00"
        ciphertext = crypto.encrypt_vote_plaintext(plaintext)
        hash_hex = crypto.hash_ciphertext(ciphertext)
        signature = crypto.sign_hash(hash_hex)
        operations = [
            ("RSA-OAEP Encryption", lambda: crypto.encrypt_vote_plaintext(plaintext)),
            ("SHA-256 Hashing", lambda: crypto.hash_ciphertext(ciphertext)),
            ("RSA-PSS Signing", lambda: crypto.sign_hash(hash_hex)),
            ("RSA-PSS Verification", lambda: crypto.verify_signature(hash_hex, signature)),
            ("Hash Verification", lambda: crypto.verify_ciphertext_hash(ciphertext, hash_hex)),
            ("RSA-OAEP Decryption", lambda: crypto.decrypt_vote_ciphertext(ciphertext)),
        ]
        for name, callback in operations:
            result = benchmark.measure_operation(name, callback)
            repo.create_record(result.operation_name, result.duration_ms, sample_size=1)
            print(f"{result.operation_name}: {result.duration_ms:.6f} ms")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
