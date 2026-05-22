from dataclasses import dataclass
from datetime import datetime

from app.domain.exceptions import MalformedVotePlaintextError


@dataclass(frozen=True)
class ParsedVotePlaintext:
    voter_id: str
    candidate_id: int
    timestamp: str


def build_vote_plaintext(voter_id: str, candidate_id: int, timestamp: str) -> str:
    return f"voter_id:{voter_id}|candidate_id:{candidate_id}|timestamp:{timestamp}"


def parse_vote_plaintext(plaintext: str) -> ParsedVotePlaintext:
    parts = plaintext.split("|")
    if len(parts) != 3:
        raise MalformedVotePlaintextError("Vote plaintext must contain voter_id, candidate_id, and timestamp")

    values: dict[str, str] = {}
    for part in parts:
        if ":" not in part:
            raise MalformedVotePlaintextError("Vote plaintext segment must use key:value format")
        key, value = part.split(":", 1)
        values[key] = value

    voter_id = values.get("voter_id")
    candidate_id_text = values.get("candidate_id")
    timestamp = values.get("timestamp")
    if not voter_id or not candidate_id_text or not timestamp:
        raise MalformedVotePlaintextError("Vote plaintext has missing required value")

    try:
        candidate_id = int(candidate_id_text)
        datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise MalformedVotePlaintextError("Vote plaintext has invalid candidate_id or timestamp") from exc

    return ParsedVotePlaintext(voter_id=voter_id, candidate_id=candidate_id, timestamp=timestamp)
