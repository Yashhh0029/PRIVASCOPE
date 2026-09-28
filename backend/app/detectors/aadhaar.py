import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

# Verhoeff algorithm tables
VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

def validate_verhoeff(num_str: str) -> bool:
    """Validates 12-digit number against Verhoeff checksum algorithm used by UIDAI."""
    c = 0
    reversed_digits = [int(d) for d in reversed(num_str)]
    for i, digit in enumerate(reversed_digits):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][digit]]
    return c == 0

class AadhaarDetector(BaseDetector):
    entity_type = "AADHAAR"
    base_severity = 10.0

    # Pattern matches 12 digits, optional space or hyphen separator, starting with 2-9
    PATTERN = re.compile(r'\b([2-9]\d{3})[\s\-]?(\d{4})[\s\-]?(\d{4})\b')
    CONTEXT_KEYWORDS = ["aadhaar", "aadhar", "uid", "uidai", "unique id", "identification number", "mera aadhaar"]

    def mask(self, value: str) -> str:
        clean = re.sub(r'\D', '', value)
        if len(clean) == 12:
            return f"XXXX XXXX {clean[-4:]}"
        return "XXXX XXXX " + (clean[-4:] if len(clean) >= 4 else "XXXX")

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0)
                clean_digits = re.sub(r'\D', '', raw_match)
                if len(clean_digits) != 12:
                    continue
                
                sources = ["regex"]
                signals = ["12-digit UID pattern matched"]
                confidence = 0.50
                
                # Check Verhoeff algorithm
                verhoeff_valid = validate_verhoeff(clean_digits)
                if verhoeff_valid:
                    sources.append("validation")
                    signals.append("Verhoeff checksum passed")
                    confidence += 0.30
                else:
                    # If Verhoeff fails, reduce confidence unless strong context proves it's a test/synthetic UID
                    confidence -= 0.15
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                if matched_kw:
                    sources.append("context")
                    signals.append(f"Context keyword matched: '{matched_kw[0]}'")
                    confidence += 0.25
                
                confidence = min(0.99, max(0.20, confidence))
                risk_level = "CRITICAL" if confidence >= 0.70 else "HIGH"

                detections.append(Detection(
                    entity_type=self.entity_type,
                    matched_value=raw_match,
                    masked_preview=self.mask(raw_match),
                    confidence=round(confidence, 2),
                    risk_level=risk_level,
                    detection_source=sources,
                    context_signals=signals,
                    location={"bbox": block.bbox, "row": block.row, "col": block.col, "col_name": block.col_name},
                    page_number=block.page,
                    sheet_name=block.sheet_name,
                    start=match.start(),
                    end=match.end(),
                    block_index=block_idx
                ))
        return detections
