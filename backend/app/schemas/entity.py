from typing import Optional, Any
from pydantic import BaseModel

class DetectedEntityResponse(BaseModel):
    id: str
    entity_type: str
    confidence: float
    risk_level: str
    masked_preview: str
    page_number: int
    sheet_name: Optional[str] = None
    location_data: Optional[Any] = None
    detection_source: Optional[list[str]] = None
    action: str

    class Config:
        from_attributes = True
