from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BenchmarkRecord(Base):
    __tablename__ = "benchmark_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    operation_name: Mapped[str] = mapped_column(String(80), nullable=False)
    duration_ms: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
