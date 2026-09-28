from dataclasses import dataclass, field
from typing import Optional, Any, List
from app.processors.base import ExtractedContent, ContentBlock

@dataclass
class Detection:
    entity_type: str
    matched_value: str
    masked_preview: str
    confidence: float  # 0.00 - 1.00
    risk_level: str    # LOW, MEDIUM, HIGH, CRITICAL
    detection_source: List[str]  # e.g., ["regex", "validation", "context"]
    context_signals: List[str]   # e.g., ["keyword: 'Aadhaar Number'", "table_column: 'UID'"]
    location: Optional[dict[str, Any]] = None  # {bbox, cell, page, etc.}
    page_number: int = 1
    sheet_name: Optional[str] = None
    start: int = 0
    end: int = 0
    block_index: int = 0

@dataclass
class DetectionContext:
    text_window_size: int = 60
    custom_patterns: dict[str, str] = field(default_factory=dict)
    enable_strict_context: bool = True

class BaseDetector:
    entity_type: str = "UNKNOWN"
    base_severity: float = 5.0

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        raise NotImplementedError

    def mask(self, value: str) -> str:
        """Default fallback masking."""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + ("*" * (len(value) - 4)) + value[-2:]
