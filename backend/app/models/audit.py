import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), index=True, nullable=True)
    action = Column(String(100), nullable=False)  # DOCUMENT_UPLOADED, SCAN_STARTED, SCAN_COMPLETED, PII_DETECTED, PROTECTION_STARTED, PROTECTION_COMPLETED, FILE_DOWNLOADED
    status = Column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, WARNING
    details = Column(Text, nullable=True)  # Strictly non-PII operational summary
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    document = relationship("Document", back_populates="audit_logs")
