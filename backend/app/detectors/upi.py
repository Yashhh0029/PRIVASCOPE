import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class UpiDetector(BaseDetector):
    entity_type = "UPI"
    base_severity = 7.0

    PATTERN = re.compile(r'\b([a-zA-Z0-9.\-_]{2,64})@([a-zA-Z]{2,30})\b')
    
    # Common UPI handles in India
    KNOWN_HANDLES = {
        "okhdfcbank", "oksbi", "okaxis", "okicici", "paytm", "ybl", "ibl", "axl", "apl",
        "upi", "barodampay", "federal", "airtel", "idfcbank", "aubank", "kotak", "postbank",
        "freecharge", "icici", "sbi", "hdfc", "axisbank", "indus", "yesbank", "centralbank"
    }
    
    COMMON_EMAIL_PROVIDERS = {
        "gmail", "yahoo", "hotmail", "outlook", "icloud", "proton", "protonmail",
        "rediffmail", "zoho", "aol", "mail", "example"
    }

    CONTEXT_KEYWORDS = ["upi", "vpa", "virtual payment address", "bhim", "gpay", "google pay", "phonepe", "paytm", "upi id", "pay via upi"]

    def mask(self, value: str) -> str:
        parts = value.strip().split("@")
        if len(parts) == 2:
            user, handle = parts
            if len(user) > 1:
                masked_user = user[0] + ("*" * (len(user) - 1))
            else:
                masked_user = user + "****"
            return f"{masked_user}@{handle}"
        return "u****@upi"

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0)
                user_part = match.group(1).lower()
                handle_part = match.group(2).lower()
                
                # Exclude standard email providers
                if handle_part in self.COMMON_EMAIL_PROVIDERS:
                    continue
                
                sources = ["regex"]
                signals = ["VPA handle syntax matched"]
                confidence = 0.50
                
                # Handle check
                if handle_part in self.KNOWN_HANDLES:
                    sources.append("validation")
                    signals.append(f"Recognized Indian PSP/Bank UPI handle: '@{handle_part}'")
                    confidence += 0.30
                else:
                    # Generic handle
                    confidence += 0.10
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                if matched_kw:
                    sources.append("context")
                    signals.append(f"Context keyword matched: '{matched_kw[0]}'")
                    confidence += 0.20
                
                # If neither a known handle nor UPI context is present, don't trigger false positives
                if handle_part not in self.KNOWN_HANDLES and not matched_kw:
                    continue
                
                confidence = min(0.99, max(0.40, confidence))
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
