import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), index=True, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, validating, extracting, ocr, detecting, context, risk, completed, failed
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    risk_explanation = Column(Text, nullable=True)
    stages_json = Column(Text, nullable=True)  # JSON-encoded array of processing stage states
    entity_count = Column(Integer, default=0)
    ocr_status = Column(String(50), default="OCR_NOT_REQUIRED")  # OCR_READY, OCR_NOT_REQUIRED, OCR_UNAVAILABLE, OCR_FAILED, OCR_COMPLETED
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    document = relationship("Document", back_populates="scans")
    user = relationship("User", back_populates="scans")
    entities = relationship("DetectedEntity", back_populates="scan", cascade="all, delete-orphan")
    protection_actions = relationship("ProtectionAction", back_populates="scan", cascade="all, delete-orphan")
