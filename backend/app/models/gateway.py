import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class GatewayAuditLog(Base):
    __tablename__ = "gateway_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    provider = Column(String(50), nullable=False)  # "local_demo", "openai", "anthropic", "gemini"
    policy_decision = Column(String(20), nullable=False)  # "ALLOW", "WARN", "PROTECT", "BLOCK"
    risk_score = Column(Float, default=0.0)
    entities_detected_count = Column(Integer, default=0)
    entity_types_json = Column(Text, nullable=True)  # JSON-encoded array: ["AADHAAR", "PHONE"]
    
    # Latency tracking (ms)
    detection_latency_ms = Column(Float, default=0.0)
    policy_latency_ms = Column(Float, default=0.0)
    tokenization_latency_ms = Column(Float, default=0.0)
    provider_latency_ms = Column(Float, default=0.0)
    total_latency_ms = Column(Float, default=0.0)
    
    # Strictly zero raw prompts and zero raw PII stored
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship
    user = relationship("User", back_populates="gateway_audits")
