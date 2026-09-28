from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.document import Document
from app.models.protection import ProtectionAction
from app.models.audit import AuditLog
from app.processors import get_processor_for_file
from app.detectors import ALL_DETECTORS, DetectionContext
from app.core.config import settings
from app.core.logger import logger

class ProtectionService:
    def apply_protection(self, db: Session, scan: Scan, mode: str, user_id: str) -> ProtectionAction:
        """
        Applies Masking or True Redaction to the document.
        Executes strict post-protection verification.
        Never reports completion until verification succeeds.
        """
        if scan.user_id != user_id:
            raise PermissionError("User does not own this scan.")

        if not scan.document_id:
            raise ValueError("Direct text scans cannot produce a downloadable file artifact.")

        document = db.query(Document).filter(Document.id == scan.document_id).first()
        if not document:
            raise FileNotFoundError("Associated document not found.")

        input_path = Path(document.storage_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Original file not found at {input_path}")

        processor = get_processor_for_file(input_path)
        if not processor:
            raise ValueError(f"No processor for format {document.file_type}")

        # Re-detect on the original file to obtain the exact target matches in memory
        extracted = processor.extract(input_path)
        det_context = DetectionContext(text_window_size=60)
        detections = []
        for detector in ALL_DETECTORS:
            detections.extend(detector.detect(extracted, det_context))

        # Collect raw values for verification
        raw_values = [d.matched_value for d in detections]

        # Prepare output path
        timestamp_str = Path(document.stored_filename).stem
        protected_filename = f"{Path(document.original_filename).stem}_PROTECTED.{document.file_type}"
        protected_storage_name = f"protected_{timestamp_str}.{document.file_type}"
        output_path = settings.PROTECTED_DIR / protected_storage_name

        # Execute protection
        success = processor.protect(input_path, output_path, detections, mode)
        if not success:
            raise RuntimeError(f"Processor failed to generate protected {document.file_type}")

        # Perform strict verification
        # For REDACT: original values must NOT be extractable
        # For MASK: raw values must NOT be extractable (only masked versions exist)
        verified = processor.verify_protection(output_path, raw_values)
        if not verified:
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError("Post-protection verification failed: sensitive values were still detectable in output artifact")

        # Record Protection Action
        action = ProtectionAction(
            scan_id=scan.id,
            document_id=document.id,
            user_id=user_id,
            mode=mode,
            output_path=str(output_path),
            output_filename=protected_filename,
            entities_protected=len(detections),
            verification_passed=True
        )
        db.add(action)

        # Log Audit Trail
        audit = AuditLog(
            user_id=user_id,
            document_id=document.id,
            action="PROTECTION_COMPLETED",
            status="SUCCESS",
            details=f"Protected {len(detections)} entities using mode '{mode}'. Verification passed."
        )
        db.add(audit)
        db.commit()
        db.refresh(action)

        logger.info(f"Protection action {action.id} completed. Protected {len(detections)} entities with mode {mode}.")
        return action

protection_service = ProtectionService()
