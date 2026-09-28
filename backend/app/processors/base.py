from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any, List

@dataclass
class ContentBlock:
    text: str
    page: int = 1
    bbox: Optional[tuple[float, float, float, float]] = None  # (x0, y0, x1, y1) or (x, y, w, h)
    source: str = "text"
    sheet_name: Optional[str] = None
    row: Optional[int] = None
    col: Optional[int] = None
    col_name: Optional[str] = None
    context_meta: dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractedContent:
    raw_text: str
    blocks: List[ContentBlock] = field(default_factory=list)
    format: str = "txt"
    metadata: dict[str, Any] = field(default_factory=dict)

class BaseProcessor:
    """Standard contract for all document processors."""
    format: str = "unknown"

    def extract(self, file_path: Path) -> ExtractedContent:
        raise NotImplementedError

    def protect(self, file_path: Path, output_path: Path, detections: list, mode: str) -> bool:
        raise NotImplementedError

    def verify_protection(self, output_path: Path, original_values: list[str]) -> bool:
        """Verifies that none of the original sensitive values can be extracted from the protected file."""
        raise NotImplementedError
