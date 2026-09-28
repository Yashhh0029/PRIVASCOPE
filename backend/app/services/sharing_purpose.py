from typing import List, Dict, Any, Union
from app.detectors.base import Detection
from app.models.entity import DetectedEntity

# Supported sharing purposes
VALID_PURPOSES = [
    "Job Application",
    "College Admission",
    "Scholarship",
    "Bank Verification",
    "Medical Document",
    "Government Form",
    "General Sharing",
    "Custom"
]

# Policy templates: Set of entity types that are legitimate to KEEP for a given purpose.
# Everything not in KEEP is recommended to PROTECT.
PURPOSE_POLICY_KEEP_MAP: Dict[str, set[str]] = {
    "Job Application": {"PHONE", "EMAIL", "STUDENT_ID"},
    "College Admission": {"PHONE", "EMAIL", "STUDENT_ID"},
    "Scholarship": {"STUDENT_ID", "PHONE", "EMAIL", "BANK_ACCOUNT", "IFSC"},
    "Bank Verification": {"PAN", "BANK_ACCOUNT", "IFSC", "PHONE", "EMAIL"},
    "Medical Document": {"PHONE", "EMAIL"},
    "Government Form": {"AADHAAR", "PAN", "PHONE", "EMAIL"},
    "General Sharing": set(),  # Protect all identifiers by default
    "Custom": set()
}

ENTITY_SENSITIVITY_DESCRIPTIONS = {
    "AADHAAR": "12-digit Indian national identity number with biometric linkage.",
    "PAN": "Permanent Account Number for Indian Income Tax and corporate identity.",
    "BANK_ACCOUNT": "Financial institution deposit/current account identifier.",
    "UPI": "Virtual Payment Address connected directly to instant bank transfer rails.",
    "IFSC": "RBI Indian Financial System Code designating bank branch routing.",
    "PHONE": "Personal telecom subscriber coordinate enabling direct voice/SMS contact.",
    "EMAIL": "Electronic mail address enabling account recovery and credential reset.",
    "STUDENT_ID": "Academic enrollment or institutional registration roll number."
}

class PurposeRecommendation:
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        matched_value_masked: str,
        what: str,
        why: str,
        evidence: str,
        risk: str,
        recommended_action: str,  # "KEEP" or "PROTECT"
        reason: str
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.matched_value_masked = matched_value_masked
        self.what = what
        self.why = why
        self.evidence = evidence
        self.risk = risk
        self.recommended_action = recommended_action
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "matched_value_masked": self.matched_value_masked,
            "what": self.what,
            "why": self.why,
            "evidence": self.evidence,
            "risk": self.risk,
            "recommended_action": self.recommended_action,
            "reason": self.reason
        }

class SharingPurposeEngine:
    def evaluate_sharing_purpose(
        self,
        purpose: str,
        entities: List[Any]
    ) -> List[PurposeRecommendation]:
        """
        Produces granular, purpose-aware KEEP vs PROTECT recommendations for each detected entity.
        Accepts either Detection objects or DetectedEntity DB records.
        """
        if not purpose or purpose not in VALID_PURPOSES:
            purpose = "General Sharing"

        keep_set = PURPOSE_POLICY_KEEP_MAP.get(purpose, set())
        recommendations: List[PurposeRecommendation] = []

        for idx, e in enumerate(entities):
            # Extract attributes dynamically from Detection or DetectedEntity
            entity_type = getattr(e, "entity_type", "UNKNOWN")
            masked_preview = getattr(e, "masked_preview", "XXXX")
            risk_level = getattr(e, "risk_level", "MEDIUM")
            entity_id = getattr(e, "id", f"entity_{idx}")

            signals = getattr(e, "context_signals", None)
            if not signals and hasattr(e, "detection_source"):
                signals = [e.detection_source] if isinstance(e.detection_source, str) else []

            is_keep = entity_type in keep_set
            action = "KEEP" if is_keep else "PROTECT"
            
            why_desc = ENTITY_SENSITIVITY_DESCRIPTIONS.get(
                entity_type,
                "Personal identifier with sensitivity exposure potential."
            )

            evidence_str = "; ".join(signals) if signals else f"Matched {entity_type} format"

            if is_keep:
                reason_str = (
                    f"The declared sharing purpose '{purpose}' typically requires {entity_type} "
                    "for legitimate operational or identity verification purposes."
                )
            else:
                reason_str = (
                    f"The declared sharing purpose '{purpose}' does not typically necessitate exposing {entity_type}. "
                    "Masking or redacting this value prevents unnecessary data leakage."
                )

            recommendations.append(PurposeRecommendation(
                entity_id=str(entity_id),
                entity_type=entity_type,
                matched_value_masked=masked_preview,
                what=entity_type,
                why=why_desc,
                evidence=evidence_str,
                risk=risk_level,
                recommended_action=action,
                reason=reason_str
            ))

        return recommendations

sharing_purpose_engine = SharingPurposeEngine()
