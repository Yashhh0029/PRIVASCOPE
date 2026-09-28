from datetime import datetime
from pydantic import BaseModel, Field

class ApplyProtectionRequest(BaseModel):
    mode: str = Field(..., pattern="^(MASK|REDACT)$")

class ProtectionResponse(BaseModel):
    id: str
    scan_id: str
    document_id: str
    mode: str
    output_filename: str
    entities_protected: int
    verification_passed: bool
    download_url: str
    created_at: datetime

    class Config:
        from_attributes = True
