import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class StudentIdDetector(BaseDetector):
    entity_type = "STUDENT_ID"
    base_severity = 3.0

    # Configurable/standard patterns found across Indian colleges and universities
    DEFAULT_PATTERNS = [
        re.compile(r'\b(20\d{2}[A-Z]{2,5}\d{3,6})\b', re.IGNORECASE),   # e.g., 2021BCSE042
        re.compile(r'\b(PRN\d{8,12})\b', re.IGNORECASE),                 # e.g., PRN1032200451
        re.compile(r'\b(ENR\d{6,12})\b', re.IGNORECASE),                 # e.g., ENR9876543
        re.compile(r'\b(ROLL[\-_]?[A-Z0-9]{4,10})\b', re.IGNORECASE),    # e.g., ROLL-4019
    ]

    CONTEXT_KEYWORDS = [
        "roll no", "roll number", "student id", "enrollment", "registration no",
        "prn", "reg no", "admission no", "scholar no", "hall ticket", "student roll"
    ]

    def mask(self, value: str) -> str:
        clean = value.strip()
        if len(clean) > 6:
            return clean[:3] + ("*" * (len(clean) - 6)) + clean[-3:]
        return clean[:1] + ("*" * (len(clean) - 2)) + clean[-1:]

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        # Merge default patterns with any dynamic custom patterns from context
        active_patterns = list(self.DEFAULT_PATTERNS)
        if context.custom_patterns.get("STUDENT_ID"):
            try:
                active_patterns.append(re.compile(context.custom_patterns["STUDENT_ID"], re.IGNORECASE))
            except Exception:
                pass

        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for pattern in active_patterns:
                for match in pattern.finditer(text):
                    raw_match = match.group(0)
                    
                    # Context Analysis
                    start_pos = max(0, match.start() - context.text_window_size)
                    end_pos = min(len(text), match.end() + context.text_window_size)
                    surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                    
                    matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                    
                    sources = ["regex"]
                    signals = [f"Matched academic identifier pattern: '{pattern.pattern}'"]
                    confidence = 0.55
                    
                    if matched_kw:
                        sources.append("context")
                        signals.append(f"Student record context matched: '{matched_kw[0]}'")
                        confidence += 0.35
                    elif block.col_name and any(kw in block.col_name.lower() for kw in self.CONTEXT_KEYWORDS):
                        sources.append("context")
                        signals.append(f"Column header matched student context: '{block.col_name}'")
                        confidence += 0.35
                    
                    confidence = min(0.99, max(0.40, confidence))
                    risk_level = "MEDIUM" if confidence >= 0.70 else "LOW"

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
