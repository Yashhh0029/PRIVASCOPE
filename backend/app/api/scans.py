import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.scan import Scan
from app.models.entity import DetectedEntity
from app.models.protection import ProtectionAction
from app.models.audit import AuditLog
from app.schemas.scan import ScanResponse, ScanStatusResponse, ScanTextRequest, ScanStage
from app.schemas.entity import DetectedEntityResponse
from app.api.deps import get_current_user
from app.services.scan_pipeline import scan_pipeline, STAGE_CONFIG
from app.core.logger import logger

router = APIRouter(prefix="/scans", tags=["Scans"])

def _format_scan_response(scan: Scan, db: Session, purpose: Optional[str] = None) -> ScanResponse:
    selected_purpose = purpose or "General Sharing"
    # Decode stages
    stages = []
    if scan.stages_json:
        try:
            stages_raw = json.loads(scan.stages_json)
            stages = [ScanStage(**s) for s in stages_raw]
        except Exception:
            stages = [ScanStage(name=s["name"], label=s["label"], status="completed" if scan.status == "completed" else "pending") for s in STAGE_CONFIG]
    else:
        stages = [ScanStage(name=s["name"], label=s["label"], status="completed" if scan.status == "completed" else "pending") for s in STAGE_CONFIG]

    # Fetch entities
    entities_db = db.query(DetectedEntity).filter(DetectedEntity.scan_id == scan.id).all()
    entity_responses = []
    for e in entities_db:
        loc = None
        if e.location_data:
            try:
                loc = json.loads(e.location_data)
            except Exception:
                loc = None
        sources = None
        if e.detection_source:
            try:
                sources = json.loads(e.detection_source)
            except Exception:
                sources = None

        entity_responses.append(DetectedEntityResponse(
            id=e.id,
            entity_type=e.entity_type,
            confidence=e.confidence,
            risk_level=e.risk_level,
            masked_preview=e.masked_preview,
            page_number=e.page_number,
            sheet_name=e.sheet_name,
            location_data=loc,
            detection_source=sources,
            action=e.action
        ))

    # Check for protection action
    prot_action = db.query(ProtectionAction).filter(ProtectionAction.scan_id == scan.id).first()

    orig_filename = scan.document.original_filename if scan.document else "pasted_text.txt"
    file_type = scan.document.file_type if scan.document else "txt"

    from app.services.sharing_purpose import sharing_purpose_engine
    from app.schemas.scan import PurposeRecommendationItem
    recs = sharing_purpose_engine.evaluate_sharing_purpose(selected_purpose, entities_db)
    rec_items = [PurposeRecommendationItem(**r.to_dict()) for r in recs]

    return ScanResponse(
        id=scan.id,
        document_id=scan.document_id,
        original_filename=orig_filename,
        file_type=file_type,
        status=scan.status,
        risk_score=scan.risk_score,
        risk_level=scan.risk_level,
        risk_explanation=scan.risk_explanation,
        sharing_purpose=selected_purpose,
        purpose_recommendations=rec_items,
        stages=stages,
        entity_count=scan.entity_count,
        ocr_status=scan.ocr_status,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        entities=entity_responses,
        has_protected_file=prot_action is not None,
        protected_action_id=prot_action.id if prot_action else None
    )

@router.post("/document/{document_id}", response_model=ScanResponse)
def scan_document(
    document_id: str,
    purpose: Optional[str] = "General Sharing",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiates full detection pipeline on an uploaded document.
    """
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Initialize scan record
    initial_stages = json.dumps([{"name": s["name"], "label": s["label"], "status": "pending"} for s in STAGE_CONFIG])
    scan = Scan(
        user_id=current_user.id,
        document_id=doc.id,
        status="pending",
        stages_json=initial_stages
    )
    db.add(scan)
    
    # Audit log
    audit_start = AuditLog(
        user_id=current_user.id,
        document_id=doc.id,
        action="SCAN_STARTED",
        status="SUCCESS",
        details=f"Scan initiated for '{doc.original_filename}'"
    )
    db.add(audit_start)
    db.commit()
    db.refresh(scan)

    # Run Pipeline synchronously
    scan = scan_pipeline.execute_scan(db, scan, document=doc)

    # Audit log for completion
    audit_end = AuditLog(
        user_id=current_user.id,
        document_id=doc.id,
        action="SCAN_COMPLETED",
        status="SUCCESS",
        details=f"Completed scan. Detected {scan.entity_count} entities. Risk: {scan.risk_score} ({scan.risk_level})"
    )
    db.add(audit_end)
    if scan.entity_count > 0:
        db.add(AuditLog(
            user_id=current_user.id,
            document_id=doc.id,
            action="PII_DETECTED",
            status="WARNING",
            details=f"Sensitive Indian PII detected: {scan.entity_count} items."
        ))
    db.commit()

    return _format_scan_response(scan, db, purpose)

@router.post("/text", response_model=ScanResponse)
def scan_text(
    req: ScanTextRequest,
    purpose: Optional[str] = "General Sharing",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiates full detection pipeline on pasted raw text.
    """
    initial_stages = json.dumps([{"name": s["name"], "label": s["label"], "status": "pending"} for s in STAGE_CONFIG])
    scan = Scan(
        user_id=current_user.id,
        document_id=None,
        status="pending",
        stages_json=initial_stages
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Run Pipeline
    scan = scan_pipeline.execute_scan(db, scan, raw_text=req.text)

    # Audit log
    db.add(AuditLog(
        user_id=current_user.id,
        action="SCAN_COMPLETED",
        status="SUCCESS",
        details=f"Direct text scan completed. Detected {scan.entity_count} entities."
    ))
    db.commit()

    return _format_scan_response(scan, db, purpose)

@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: str,
    purpose: Optional[str] = "General Sharing",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches full scan result, entities, and risk evaluation for authenticated user."""
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    return _format_scan_response(scan, db, purpose)

@router.get("/{scan_id}/status", response_model=ScanStatusResponse)
def get_scan_status(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lightweight endpoint for polling scan progress stages."""
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    stages = []
    if scan.stages_json:
        try:
            stages_raw = json.loads(scan.stages_json)
            stages = [ScanStage(**s) for s in stages_raw]
        except Exception:
            stages = []

    return ScanStatusResponse(
        id=scan.id,
        status=scan.status,
        stages=stages,
        ocr_status=scan.ocr_status,
        risk_score=scan.risk_score,
        risk_level=scan.risk_level
    )
