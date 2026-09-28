import re
from typing import List
from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.processors.base import ExtractedContent

class IfscDetector(BaseDetector):
    entity_type = "IFSC"
    base_severity = 5.0

    # 11 characters: 4 letters, '0', 6 alphanumeric
    PATTERN = re.compile(r'\b([A-Z]{4}0[A-Z0-9]{6})\b')

    MAJOR_BANK_CODES = {
        "SBIN", "HDFC", "ICIC", "UTIB", "PUNB", "BARB", "KKBK", "CNRB",
        "UBIN", "IOBA", "IDIB", "YESB", "IDFB", "FDRL", "INDB", "MAHB",
        "BOM", "CORP", "SYNB", "VIJB", "ALLA", "ANDB", "BKDN", "ORBC"
    }

    CONTEXT_KEYWORDS = ["ifsc", "ifsc code", "rtgs", "neft", "branch code", "bank branch", "imps", "bank ifsc"]

    def mask(self, value: str) -> str:
        clean = value.strip().upper()
        if len(clean) == 11:
            return clean[:6] + "*****"
        return "IFSC00*****"

    def detect(self, content: ExtractedContent, context: DetectionContext) -> List[Detection]:
        detections: List[Detection] = []
        
        for block_idx, block in enumerate(content.blocks):
            text = block.text
            for match in self.PATTERN.finditer(text):
                raw_match = match.group(0).upper()
                bank_code = raw_match[:4]
                
                sources = ["regex"]
                signals = ["RBI standard 11-char IFSC format (4 alpha + 0 + 6 alphanum)"]
                confidence = 0.65
                
                # Bank code recognition
                if bank_code in self.MAJOR_BANK_CODES:
                    sources.append("validation")
                    signals.append(f"Recognized RBI Bank identifier prefix: '{bank_code}'")
                    confidence += 0.20
                
                # Context Analysis
                start_pos = max(0, match.start() - context.text_window_size)
                end_pos = min(len(text), match.end() + context.text_window_size)
                surrounding = (text[start_pos:end_pos] + " " + (block.col_name or "") + " " + (block.sheet_name or "")).lower()
                
                matched_kw = [kw for kw in self.CONTEXT_KEYWORDS if kw in surrounding]
                if matched_kw:
                    sources.append("context")
                    signals.append(f"Context keyword matched: '{matched_kw[0]}'")
                    confidence += 0.15
                
                confidence = min(0.99, max(0.40, confidence))
                risk_level = "HIGH" if confidence >= 0.80 else "MEDIUM"

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
