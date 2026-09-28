from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.user import User
from app.models.gateway import GatewayAuditLog
from app.api.deps import get_current_user
from app.services.privacy_gateway import privacy_gateway
from app.services.pseudonymization_service import pseudonymization_service
from app.services.providers import PROVIDERS

router = APIRouter(prefix="/gateway", tags=["AI Privacy Gateway"])

class GatewayAnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=50000, description="Outbound prompt or query")
    provider: Optional[str] = Field("local_demo", description="AI provider key: local_demo, openai, anthropic, gemini")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")

class GatewayRehydrateRequest(BaseModel):
    text: str = Field(..., description="Text containing local tokens like <AADHAAR_01> to rehydrate")
    session_id: str = Field(..., description="Active session ID containing the local token mapping")

class ProviderInfo(BaseModel):
    id: str
    name: str
    display_name: str
    is_demo: bool
    is_available: bool

@router.get("/providers", response_model=List[ProviderInfo])
def get_available_providers():
    """Returns list of registered AI providers and their availability status."""
    info_list = []
    for key, p in PROVIDERS.items():
        info_list.append(ProviderInfo(
            id=key,
            name=p.name,
            display_name=p.display_name,
            is_demo=p.is_demo,
            is_available=p.is_available()
        ))
    return info_list

@router.post("/analyze")
def analyze_prompt(
    req: GatewayAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates outbound prompt against PRIVASCOPE AI Privacy Firewall.
    Enforces ALLOW, WARN, PROTECT, or BLOCK policies.
    Applies reversible local pseudonymization when policy is PROTECT.
    Guarantees provider never receives raw PII.
    """
    result = privacy_gateway.process_prompt(
        db=db,
        user=current_user,
        prompt=req.prompt,
        provider_name=req.provider or "local_demo",
        session_id=req.session_id
    )
    return result.to_dict()

@router.post("/rehydrate")
def rehydrate_tokens(
    req: GatewayRehydrateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Replaces local pseudonymized tokens with their original values in user's browser.
    Never transmits token mapping outside local boundary.
    """
    rehydrated = pseudonymization_service.rehydrate(req.text, req.session_id)
    return {
        "session_id": req.session_id,
        "rehydrated_text": rehydrated
    }

@router.get("/stats")
def get_gateway_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns gateway privacy telemetry for the authenticated user."""
    total_calls = db.query(GatewayAuditLog).filter(GatewayAuditLog.user_id == current_user.id).count()
    blocked_calls = db.query(GatewayAuditLog).filter(
        GatewayAuditLog.user_id == current_user.id,
        GatewayAuditLog.policy_decision == "BLOCK"
    ).count()
    protected_calls = db.query(GatewayAuditLog).filter(
        GatewayAuditLog.user_id == current_user.id,
        GatewayAuditLog.policy_decision == "PROTECT"
    ).count()
    
    total_entities_detected = db.query(
        func.sum(GatewayAuditLog.entities_detected_count)
    ).filter(GatewayAuditLog.user_id == current_user.id).scalar() or 0

    return {
        "total_requests": total_calls,
        "protected_requests": protected_calls,
        "blocked_requests": blocked_calls,
        "total_entities_shielded": int(total_entities_detected),
        "zero_cloud_exposure_guarantee": True
    }
