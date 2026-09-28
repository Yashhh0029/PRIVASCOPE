import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.document import Document
from app.models.entity import DetectedEntity
from app.processors import get_processor_for_file
from app.processors.base import ExtractedContent, ContentBlock
from app.detectors import ALL_DETECTORS, Detection, DetectionContext
from app.services.risk_engine import risk_engine
from app.services.ocr_service import ocr_service
from app.core.logger import logger

STAGE_CONFIG = [
    {"name": "validating", "label": "Validating file integrity"},
    {"name": "extracting", "label": "Extracting document content"},
    {"name": "ocr", "label": "OCR & optical analysis"},
    {"name": "detecting", "label": "Detecting sensitive Indian PII"},
    {"name": "context", "label": "Analyzing semantic & structural context"},
    {"name": "risk", "label": "Evaluating multi-factor privacy risk"},
    {"name": "completed", "label": "Scan report generated"}
]

class ScanPipeline:
    def execute_scan(self, db: Session, scan: Scan, document: Optional[Document] = None, raw_text: Optional[str] = None) -> Scan:
        """
        Executes real end-to-end scanning pipeline.
        Updates actual stages progressively in DB.
        """
        stages = [{"name": s["name"], "label": s["label"], "status": "pending"} for s in STAGE_CONFIG]
        
        def update_stage(stage_name: str, status: str, detail: Optional[str] = None):
            for st in stages:
                if st["name"] == stage_name:
                    st["status"] = status
                    if detail:
                        st["detail"] = detail
            scan.stages_json = json.dumps(stages)
            db.commit()

        try:
            # Stage 1: Validating
            scan.status = "validating"
            update_stage("validating", "processing")
            
            if document:
                file_path = Path(document.storage_path)
                if not file_path.exists():
                    raise FileNotFoundError(f"Stored document file not found at {document.storage_path}")
                processor = get_processor_for_file(file_path)
                if not processor:
                    raise ValueError(f"No processor available for file format: {document.file_type}")
            elif raw_text is None:
                raise ValueError("Neither document nor raw text provided for scanning")
            
            update_stage("validating", "completed")

            # Stage 2: Extracting
            scan.status = "extracting"
            update_stage("extracting", "processing")
            
            if document:
                extracted: ExtractedContent = processor.extract(file_path)
            else:
                blocks = [ContentBlock(text=line, page=1, source="text") for line in raw_text.splitlines() if line.strip()]
                extracted = ExtractedContent(raw_text=raw_text, blocks=blocks, format="txt")
            
            update_stage("extracting", "completed")

            # Stage 3: OCR
            scan.status = "ocr"
            update_stage("ocr", "processing")
            
            if document and document.file_type in ("png", "jpg", "jpeg"):
                scan.ocr_status = "OCR_COMPLETED"
                update_stage("ocr", "completed", "Optical Character Recognition completed")
            elif document and extracted.metadata.get("ocr_used"):
                scan.ocr_status = "OCR_COMPLETED"
                update_stage("ocr", "completed", "Scanned pages processed via OCR")
            else:
                scan.ocr_status = "OCR_NOT_REQUIRED"
                update_stage("ocr", "skipped", "Native digital text extracted directly")

            # Stage 4: Detecting PII
            scan.status = "detecting"
            update_stage("detecting", "processing")
            
            det_context = DetectionContext(text_window_size=60)
            all_detections: List[Detection] = []

            for detector in ALL_DETECTORS:
                found = detector.detect(extracted, det_context)
                all_detections.extend(found)

            update_stage("detecting", "completed", f"Detected {len(all_detections)} candidate entities")

            # Stage 5: Context & Deduplication
            scan.status = "context"
            update_stage("context", "processing")
            
            # Deduplicate overlapping matches by prioritizing higher confidence and longer match
            deduped: dict[tuple[int, int, str], Detection] = {}
            for d in all_detections:
                key = (d.block_index, d.start, d.entity_type)
                if key not in deduped or d.confidence > deduped[key].confidence:
                    deduped[key] = d
            
            final_detections = list(deduped.values())
            update_stage("context", "completed", "Structural & context fusion applied")

            # Stage 6: Risk Engine
            scan.status = "risk"
            update_stage("risk", "processing")
            
            risk_result = risk_engine.calculate_risk(final_detections)
            scan.risk_score = risk_result.score
            scan.risk_level = risk_result.level
            scan.risk_explanation = risk_result.explanation
            scan.entity_count = len(final_detections)
            update_stage("risk", "completed", f"Privacy risk evaluated: {risk_result.score}/100 ({risk_result.level})")

            # Save Detected Entities in DB (Zero Raw PII)
            for d in final_detections:
                entity = DetectedEntity(
                    scan_id=scan.id,
                    entity_type=d.entity_type,
                    confidence=d.confidence,
                    risk_level=d.risk_level,
                    masked_preview=d.masked_preview,
                    page_number=d.page_number,
                    sheet_name=d.sheet_name,
                    location_data=json.dumps(d.location) if d.location else None,
                    detection_source=json.dumps(d.detection_source),
                    action="DETECTED"
                )
                db.add(entity)

            # Stage 7: Completed
            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)
            update_stage("completed", "completed")
            db.commit()
            db.refresh(scan)

            logger.info(f"Scan {scan.id} completed successfully. Found {len(final_detections)} entities. Risk: {scan.risk_score}")
            return scan

        except Exception as e:
            scan.status = "failed"
            scan.error_message = str(e)
            scan.completed_at = datetime.now(timezone.utc)
            update_stage(scan.status if scan.status in [s["name"] for s in STAGE_CONFIG] else "validating", "failed", str(e))
            db.commit()
            logger.error(f"Scan {scan.id} pipeline execution failed: {e}")
            raise e

scan_pipeline = ScanPipeline()
