from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.entity import DetectedEntity
from app.models.protection import ProtectionAction
from app.models.document import Document
from app.schemas.dashboard import DashboardStatsResponse, RecentScanItem
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Computes dashboard analytics derived exclusively from real database records.
    Never returns fabricated metrics.
    """
    user_id = current_user.id

    # 1. Total Scans
    total_scans = db.query(func.count(Scan.id)).filter(Scan.user_id == user_id).scalar() or 0

    # 2. Protected Documents
    protected_docs = db.query(func.count(ProtectionAction.id)).filter(ProtectionAction.user_id == user_id).scalar() or 0

    # 3. High/Critical Risk Scans
    high_risk_docs = db.query(func.count(Scan.id)).filter(
        Scan.user_id == user_id,
        Scan.risk_level.in_(["HIGH", "CRITICAL"])
    ).scalar() or 0

    # 4. Total Entities Detected
    total_entities = db.query(func.count(DetectedEntity.id)).join(Scan).filter(Scan.user_id == user_id).scalar() or 0

    # 5. PII Distribution
    pii_counts_query = (
        db.query(DetectedEntity.entity_type, func.count(DetectedEntity.id))
        .join(Scan)
        .filter(Scan.user_id == user_id)
        .group_by(DetectedEntity.entity_type)
        .all()
    )
    pii_dist = {
        "AADHAAR": 0, "PAN": 0, "PHONE": 0, "EMAIL": 0,
        "UPI": 0, "IFSC": 0, "BANK_ACCOUNT": 0, "STUDENT_ID": 0
    }
    for etype, count in pii_counts_query:
        pii_dist[etype] = count

    # 6. Risk Distribution
    risk_counts_query = (
        db.query(Scan.risk_level, func.count(Scan.id))
        .filter(Scan.user_id == user_id)
        .group_by(Scan.risk_level)
        .all()
    )
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for rlevel, count in risk_counts_query:
        if rlevel in risk_dist:
            risk_dist[rlevel] = count

    # 7. Recent Scans
    recent_scans_db = (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(desc(Scan.created_at))
        .limit(10)
        .all()
    )
    recent_scans: List[RecentScanItem] = []
    for s in recent_scans_db:
        has_protected = db.query(ProtectionAction).filter(ProtectionAction.scan_id == s.id).first() is not None
        fname = s.document.original_filename if s.document else "Direct Text Scan"
        ftype = s.document.file_type if s.document else "txt"
        recent_scans.append(RecentScanItem(
            id=s.id,
            document_id=s.document_id,
            filename=fname,
            file_type=ftype,
            scan_date=s.created_at,
            risk_score=s.risk_score,
            risk_level=s.risk_level,
            entity_count=s.entity_count,
            status=s.status,
            has_protected_file=has_protected
        ))

    return DashboardStatsResponse(
        total_scans=total_scans,
        protected_documents=protected_docs,
        high_risk_documents=high_risk_docs,
        total_entities_detected=total_entities,
        pii_distribution=pii_dist,
        risk_distribution=risk_dist,
        recent_scans=recent_scans
    )

@router.get("/history", response_model=List[RecentScanItem])
def get_scan_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paginated list of scans performed by the authenticated user."""
    offset = (page - 1) * limit
    scans_db = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(desc(Scan.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for s in scans_db:
        has_protected = db.query(ProtectionAction).filter(ProtectionAction.scan_id == s.id).first() is not None
        fname = s.document.original_filename if s.document else "Direct Text Scan"
        ftype = s.document.file_type if s.document else "txt"
        items.append(RecentScanItem(
            id=s.id,
            document_id=s.document_id,
            filename=fname,
            file_type=ftype,
            scan_date=s.created_at,
            risk_score=s.risk_score,
            risk_level=s.risk_level,
            entity_count=s.entity_count,
            status=s.status,
            has_protected_file=has_protected
        ))
    return items
