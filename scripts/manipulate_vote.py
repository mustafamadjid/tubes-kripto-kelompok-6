import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.vote_record import VoteRecord


def flip_first_byte(value: bytes) -> bytes:
    if not value:
        return value
    data = bytearray(value)
    data[0] ^= 0x01
    return bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manipulate a vote record for demo purposes")
    parser.add_argument("vote_id")
    parser.add_argument("field", choices=["ciphertext", "hash", "signature"])
    args = parser.parse_args()

    db = SessionLocal()
    try:
        vote = db.get(VoteRecord, args.vote_id)
        if vote is None:
            raise SystemExit(f"Vote {args.vote_id} not found")
        if args.field == "ciphertext":
            vote.ciphertext = flip_first_byte(vote.ciphertext)
        elif args.field == "hash":
            vote.ciphertext_hash = ("0" if vote.ciphertext_hash[0] != "0" else "1") + vote.ciphertext_hash[1:]
        else:
            vote.signature = flip_first_byte(vote.signature)
        db.commit()
        print(f"Manipulated {args.field} for vote {args.vote_id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
