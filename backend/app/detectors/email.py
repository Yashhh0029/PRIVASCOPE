import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class EmailDetector(BaseDetector):
    entity_type = "EMAIL"
    base_severity = 3.0

    PATTERN = re.compile(r'\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b')
    CONTEXT_KEYWORDS = ["email", "e-mail", "mail", "contact", "email address", "to:", "from:"]

    def mask(self, value: str) -> str:
        parts = value.strip().split("@")
        if len(parts) == 2:
            user, domain = parts
            if len(user) > 1:
                masked_user = user[0] + "****"
            else:
                masked_user = user + "****"
            return f"{masked_user}@{domain}"
        return "e****@domain.com"

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0)
                
                # Validation checks
                if ".." in raw_match or raw_match.endswith("."):
                    continue
                parts = raw_match.split("@")
                if len(parts) != 2 or "." not in parts[1]:
                    continue
                tld = parts[1].split(".")[-1]
                if len(tld) < 2 or not tld.isalpha():
                    continue

                sources = ["regex", "validation"]
                signals = ["RFC-compliant email pattern", "Valid domain and TLD structure"]
                confidence = 0.85
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                if matched_kw:
                    sources.append("context")
                    signals.append(f"Context keyword matched: '{matched_kw[0]}'")
                    confidence += 0.14
                
                confidence = min(0.99, max(0.50, confidence))
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
