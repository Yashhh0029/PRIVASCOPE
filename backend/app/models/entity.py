import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class DetectedEntity(Base):
    __tablename__ = "detected_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id"), index=True, nullable=False)
    entity_type = Column(String(50), nullable=False)  # AADHAAR, PAN, PHONE, EMAIL, UPI, IFSC, BANK_ACCOUNT, STUDENT_ID
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    risk_level = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    masked_preview = Column(String(255), nullable=False)  # NEVER store raw PII in database
    page_number = Column(Integer, default=1)
    sheet_name = Column(String(255), nullable=True)
    location_data = Column(Text, nullable=True)  # JSON-encoded bbox: {x, y, width, height} or cell: "B12"
    detection_source = Column(Text, nullable=True)  # JSON-encoded array: ["regex", "validation", "context"]
    action = Column(String(50), default="DETECTED")  # DETECTED, MASKED, REDACTED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship
    scan = relationship("Scan", back_populates="entities")
