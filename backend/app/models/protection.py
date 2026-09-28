import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProtectionAction(Base):
    __tablename__ = "protection_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id"), index=True, nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    mode = Column(String(50), nullable=False)  # MASK, REDACT
    output_path = Column(String(500), nullable=False)
    output_filename = Column(String(255), nullable=False)
    entities_protected = Column(Integer, default=0, nullable=False)
    verification_passed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    scan = relationship("Scan", back_populates="protection_actions")
    document = relationship("Document", back_populates="protection_actions")
