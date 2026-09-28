from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.document import Document
from app.models.protection import ProtectionAction
from app.models.entity import DetectedEntity
from app.models.audit import AuditLog
from app.schemas.protection import ApplyProtectionRequest, ProtectionResponse
from app.api.deps import get_current_user
from app.services.protection_service import protection_service
from app.core.logger import logger

router = APIRouter(prefix="/protection", tags=["Protection"])

@router.post("/{scan_id}/apply", response_model=ProtectionResponse)
def apply_protection(
    scan_id: str,
    req: ApplyProtectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Applies masking or true redaction to the document.
    Executes automated post-protection verification before marking complete.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    if scan.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scan has not finished processing.")

    try:
        action = protection_service.apply_protection(db, scan, mode=req.mode, user_id=current_user.id)
        
        download_url = f"/api/protection/{action.id}/download"
        return ProtectionResponse(
            id=action.id,
            scan_id=action.scan_id,
            document_id=action.document_id,
            mode=action.mode,
            output_filename=action.output_filename,
            entities_protected=action.entities_protected,
            verification_passed=action.verification_passed,
            download_url=download_url,
            created_at=action.created_at
        )
    except Exception as e:
        logger.error(f"Failed to apply protection for scan {scan_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{action_id}/download")
def download_protected_file(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Streams the verified protected file with strict ownership validation.
    Never accepts arbitrary paths from client.
    """
    action = db.query(ProtectionAction).filter(
        ProtectionAction.id == action_id,
        ProtectionAction.user_id == current_user.id
    ).first()

    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protected artifact not found.")

    file_path = Path(action.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file missing from storage.")

    # Log audit event
    audit = AuditLog(
        user_id=current_user.id,
        document_id=action.document_id,
        action="FILE_DOWNLOADED",
        status="SUCCESS",
        details=f"Downloaded protected file: '{action.output_filename}'"
    )
    db.add(audit)
    db.commit()

    logger.info(f"User {current_user.email} downloaded protected file: {action.output_filename}")
    return FileResponse(
        path=file_path,
        filename=action.output_filename,
        media_type="application/octet-stream"
    )

@router.get("/{scan_id}/diff")
def get_protection_diff(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns original vs protected representation for UI side-by-side inspection.
    Masks the original side with standard privacy markers for safety.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    entities = db.query(DetectedEntity).filter(DetectedEntity.scan_id == scan.id).all()
    diff_items = []
    for e in entities:
        diff_items.append({
            "type": e.entity_type,
            "masked_preview": e.masked_preview,
            "redacted_preview": "[REDACTED]",
            "page_or_sheet": e.sheet_name or f"Page {e.page_number}",
            "confidence": e.confidence
        })

    return {"scan_id": scan.id, "diff_items": diff_items}
