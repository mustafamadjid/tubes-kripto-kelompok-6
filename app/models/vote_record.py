from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.domain.enums import VerificationStatus


class VoteRecord(Base):
    __tablename__ = "vote_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    voter_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    ciphertext_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), default=VerificationStatus.PENDING.value)
    manipulation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
