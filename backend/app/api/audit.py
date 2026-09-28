from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.dashboard import AuditLogItem
from app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("", response_model=List[AuditLogItem])
@router.get("/logs", response_model=List[AuditLogItem])
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns immutable audit logs of document operations for compliance verification.
    """
    offset = (page - 1) * limit
    logs_db = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(desc(AuditLog.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for l in logs_db:
        fname = l.document.original_filename if l.document else None
        items.append(AuditLogItem(
            id=l.id,
            action=l.action,
            status=l.status,
            details=l.details,
            created_at=l.created_at,
            document_id=l.document_id,
            filename=fname
        ))
    return items
