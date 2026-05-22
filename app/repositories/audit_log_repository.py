from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(self, event_type: str, entity_type: str, entity_id: str | None, message: str) -> AuditLog:
        log = AuditLog(event_type=event_type, entity_type=entity_type, entity_id=entity_id, message=message)
        self.db.add(log)
        return log

    def find_all(self) -> list[AuditLog]:
        return list(self.db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all())

    def count_all(self) -> int:
        return len(self.find_all())
