from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field
from app.schemas.entity import DetectedEntityResponse

class ScanStage(BaseModel):
    name: str
    label: str
    status: str  # pending, processing, completed, failed, skipped
    detail: Optional[str] = None

class PurposeRecommendationItem(BaseModel):
    entity_id: str
    entity_type: str
    matched_value_masked: str
    what: str
    why: str
    evidence: str
    risk: str
    recommended_action: str  # "KEEP" or "PROTECT"
    reason: str

class ScanTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000)
    sharing_purpose: Optional[str] = "General Sharing"

class ScanDocumentRequest(BaseModel):
    sharing_purpose: Optional[str] = "General Sharing"

class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    id: str
    document_id: Optional[str] = None
    original_filename: Optional[str] = None
    file_type: Optional[str] = None
    status: str
    risk_score: float
    risk_level: str
    risk_explanation: Optional[str] = None
    sharing_purpose: Optional[str] = "General Sharing"
    purpose_recommendations: List[PurposeRecommendationItem] = []
    stages: list[ScanStage]
    entity_count: int
    ocr_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    entities: list[DetectedEntityResponse] = []
    has_protected_file: bool = False
    protected_action_id: Optional[str] = None

    class Config:
        from_attributes = True

class ScanStatusResponse(BaseModel):
    id: str
    status: str
    stages: list[ScanStage]
    ocr_status: str
    risk_score: float
    risk_level: str
