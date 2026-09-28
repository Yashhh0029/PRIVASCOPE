import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class PanDetector(BaseDetector):
    entity_type = "PAN"
    base_severity = 8.0

    PATTERN = re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b')
    VALID_ENTITY_TYPES = set("PCHFATBLJG")
    CONTEXT_KEYWORDS = ["pan", "permanent account number", "income tax", "pan card", "nsdl", "utiitsl", "tax id"]

    def mask(self, value: str) -> str:
        clean = value.strip().upper()
        if len(clean) == 10:
            return f"XXXXX****{clean[-1]}"
        return "XXXXX****X"

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0).upper()
                
                sources = ["regex"]
                signals = ["Standard 10-char PAN alphanumeric format"]
                confidence = 0.60
                
                # 4th character validation
                fourth_char = raw_match[3]
                if fourth_char in self.VALID_ENTITY_TYPES:
                    sources.append("validation")
                    signals.append(f"Entity category '{fourth_char}' is valid Indian Income Tax designation")
                    confidence += 0.20
                else:
                    confidence -= 0.15
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                if matched_kw:
                    sources.append("context")
                    signals.append(f"Context keyword matched: '{matched_kw[0]}'")
                    confidence += 0.20
                
                confidence = min(0.99, max(0.25, confidence))
                risk_level = "HIGH" if confidence >= 0.70 else "MEDIUM"

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
