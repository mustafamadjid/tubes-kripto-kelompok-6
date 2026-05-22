from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.benchmark_record import BenchmarkRecord


class BenchmarkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_record(
        self,
        operation_name: str,
        duration_ms: float,
        sample_size: int | None = None,
        metadata_json: dict | None = None,
    ) -> BenchmarkRecord:
        record = BenchmarkRecord(
            operation_name=operation_name,
            duration_ms=duration_ms,
            sample_size=sample_size,
            metadata_json=metadata_json,
        )
        self.db.add(record)
        return record

    def find_all(self) -> list[BenchmarkRecord]:
        return list(self.db.scalars(select(BenchmarkRecord).order_by(BenchmarkRecord.created_at.desc())).all())
