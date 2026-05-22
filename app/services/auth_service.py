import hashlib
import hmac

from app.config import settings


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, voter_repository=None) -> None:
        self.voter_repository = voter_repository

    def authenticate_voter(self, voter_id: str, password: str):
        if self.voter_repository is None:
            return None
        voter = self.voter_repository.find_by_voter_id(voter_id)
        if voter is None:
            return None
        if hmac.compare_digest(voter.password_hash, hash_password(password)):
            return voter
        return None

    def authenticate_admin(self, username: str, password: str) -> bool:
        return hmac.compare_digest(username, settings.admin_username) and hmac.compare_digest(
            password,
            settings.admin_password,
        )
