import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class PhoneDetector(BaseDetector):
    entity_type = "PHONE"
    base_severity = 4.0

    # Indian mobile: 10 digits starting with 6, 7, 8, 9, optional +91 or 0 prefix
    PATTERN = re.compile(r'(?:\+91[\-\s]?|0)?\b([6789]\d{9})\b')
    
    POSITIVE_KEYWORDS = [
        "phone", "mobile", "contact", "call", "whatsapp", "tel", "cell",
        "ph no", "ph.", "m.no", "phone number", "mobile number", "contact no",
        "calling", "helpline", "handset", "sim"
    ]

    # Expanded structural negative categories: transaction, application, registration, educational IDs
    NEGATIVE_KEYWORDS = [
        # Commercial / Transactions
        "order", "txn", "transaction", "invoice", "ref", "reference", "account",
        "serial", "pnr", "tracking", "hash", "code", "batch", "bill", "receipt",
        # Academic / Application / Registrations (solves Application No false positive)
        "application", "application no", "application number", "app no", "appl no",
        "registration", "registration no", "reg no", "reg. no", "roll no", "roll number",
        "student id", "student no", "prn", "enrolment", "enrollment", "admit card",
        "hall ticket", "candidate id", "applicant id", "merchant id", "gateway"
    ]

    def mask(self, value: str) -> str:
        clean = re.sub(r'\D', '', value)
        if len(clean) >= 10:
            last_3 = clean[-3:]
            return "XXXXXXX" + last_3
        return "XXXXXXX" + (clean[-3:] if len(clean) >= 3 else "XXX")

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0)
                clean_digits = match.group(1)
                
                # Check surrounding text
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                # Immediate prefix check (immediate label right before match)
                pre_start = max(0, match.start() - 35)
                immediate_pre = text[pre_start:match.start()].lower()

                has_negative = any(neg in surrounding for neg in self.NEGATIVE_KEYWORDS) or any(neg in immediate_pre for neg in self.NEGATIVE_KEYWORDS)
                has_positive = any(pos in surrounding for pos in self.POSITIVE_KEYWORDS) or any(pos in immediate_pre for pos in self.POSITIVE_KEYWORDS)
                
                # If negative context is detected (e.g. Order ID, Application No, Transaction ID) and NO explicit phone keyword is present, SUPPRESS!
                if has_negative and not has_positive:
                    continue
                
                sources = ["regex"]
                signals = ["10-digit Indian telecom prefix (6-9) pattern matched"]
                confidence = 0.55
                
                if has_positive:
                    sources.append("context")
                    matched_kw = [pos for pos in self.POSITIVE_KEYWORDS if pos in surrounding][0]
                    signals.append(f"Phone context matched: '{matched_kw}'")
                    confidence += 0.40
                elif not has_negative:
                    # Generic standalone number
                    confidence += 0.15
                    signals.append("Standalone phone-compatible sequence")

                confidence = min(0.99, max(0.25, confidence))
                risk_level = "HIGH" if confidence >= 0.80 else ("MEDIUM" if confidence >= 0.50 else "LOW")

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
