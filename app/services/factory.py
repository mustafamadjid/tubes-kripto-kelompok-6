from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.vote_repository import VoteRepository
from app.repositories.voter_repository import VoterRepository
from app.services.crypto_service import CryptoService
from app.services.recapitulation_service import RecapitulationService
from app.services.voting_service import VotingService


def create_crypto_service() -> CryptoService:
    required_paths = [
        settings.admin_private_key_path,
        settings.admin_public_key_path,
        settings.system_private_key_path,
        settings.system_public_key_path,
    ]
    missing = [path for path in required_paths if not Path(path).exists()]
    if missing:
        raise FileNotFoundError("RSA key files are missing. Run: python scripts/generate_keys.py")
    return CryptoService(
        settings.admin_private_key_path,
        settings.admin_public_key_path,
        settings.system_private_key_path,
        settings.system_public_key_path,
    )


def create_voting_service(db: Session) -> VotingService:
    return VotingService(
        voter_repository=VoterRepository(db),
        candidate_repository=CandidateRepository(db),
        vote_repository=VoteRepository(db),
        audit_log_repository=AuditLogRepository(db),
        crypto_service=create_crypto_service(),
    )


def create_recapitulation_service(db: Session) -> RecapitulationService:
    return RecapitulationService(
        vote_repository=VoteRepository(db),
        candidate_repository=CandidateRepository(db),
        audit_log_repository=AuditLogRepository(db),
        crypto_service=create_crypto_service(),
    )
