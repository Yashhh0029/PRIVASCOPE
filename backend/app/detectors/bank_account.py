import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class BankAccountDetector(BaseDetector):
    entity_type = "BANK_ACCOUNT"
    base_severity = 8.0

    # Indian bank accounts range between 9 and 18 numeric digits
    PATTERN = re.compile(r'\b(\d{9,18})\b')

    # Strict banking keywords required to prevent false positives
    BANKING_KEYWORDS = [
        "account", "a/c", "acct", "savings", "current", "beneficiary",
        "bank account", "acc no", "acc. no", "account number", "cif", "sb a/c", "ca a/c",
        "beneficiary account", "credit to a/c"
    ]

    NEGATIVE_KEYWORDS = ["pin", "zip", "postal", "order", "invoice", "barcode", "tracking", "txn id", "transaction id"]

    def mask(self, value: str) -> str:
        clean = re.sub(r'\D', '', value)
        if len(clean) >= 4:
            return ("X" * (len(clean) - 4)) + clean[-4:]
        return "XXXXXXXXXXXX"

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0)
                clean_digits = re.sub(r'\D', '', raw_match)
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                # Check negative signals
                if any(neg in surrounding for neg in self.NEGATIVE_KEYWORDS):
                    continue

                # Conservative Rule: MUST have positive banking context
                matched_kw = [kw for kw in self.BANKING_KEYWORDS if kw in surrounding]
                if not matched_kw:
                    # In strict mode, reject any naked 9-18 digit number as a bank account
                    continue
                
                sources = ["regex", "context"]
                signals = [
                    f"9-18 digit numeric account length ({len(clean_digits)} digits)",
                    f"Mandatory banking context matched: '{matched_kw[0]}'"
                ]
                confidence = 0.70
                
                # If specific phrases like "account number" or "a/c no" appear, raise confidence
                if any(strong in surrounding for strong in ["account number", "a/c no", "bank account", "beneficiary"]):
                    confidence += 0.20
                    signals.append("High-specificity banking keyword confirmed")

                confidence = min(0.99, max(0.50, confidence))
                risk_level = "CRITICAL" if confidence >= 0.85 else "HIGH"

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
