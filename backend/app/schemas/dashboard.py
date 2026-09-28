from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RecentScanItem(BaseModel):
    id: str
    document_id: Optional[str] = None
    filename: str
    file_type: str
    scan_date: datetime
    risk_score: float
    risk_level: str
    entity_count: int
    status: str
    has_protected_file: bool

class DashboardStatsResponse(BaseModel):
    total_scans: int
    protected_documents: int
    high_risk_documents: int
    total_entities_detected: int
    pii_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    recent_scans: list[RecentScanItem]

class AuditLogItem(BaseModel):
    id: str
    action: str
    status: str
    details: Optional[str]
    created_at: datetime
    document_id: Optional[str]
    filename: Optional[str] = None
