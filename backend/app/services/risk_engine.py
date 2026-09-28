from typing import List, Dict, Any
from app.detectors.base import Detection
from app.core.config import settings

class RiskCalculationResult:
    def __init__(self, score: float, level: str, explanation: str, breakdown: Dict[str, Any]):
        self.score = score
        self.level = level
        self.explanation = explanation
        self.breakdown = breakdown

class RiskEngine:
    """
    Transparent, explainable risk scoring engine for Indian Personal Data.
    Follows application product policy weights and compounding exposure penalties.
    """
    POLICY_DISCLAIMER = (
        "PRIVASCOPE's risk score is an application-defined risk model intended "
        "to prioritize privacy protection actions. It is not an official government risk classification."
    )

    SEVERITY_WEIGHTS = {
        "AADHAAR": settings.WEIGHT_AADHAAR,         # 10.0
        "PAN": settings.WEIGHT_PAN,                 # 8.0
        "BANK_ACCOUNT": settings.WEIGHT_BANK_ACCOUNT, # 8.0
        "UPI": settings.WEIGHT_UPI,                 # 7.0
        "IFSC": settings.WEIGHT_IFSC,               # 5.0
        "PHONE": settings.WEIGHT_PHONE,             # 4.0
        "EMAIL": settings.WEIGHT_EMAIL,             # 3.0
        "STUDENT_ID": settings.WEIGHT_STUDENT_ID,   # 3.0
    }

    IDENTITY_TYPES = {"AADHAAR", "PAN", "STUDENT_ID"}
    FINANCIAL_TYPES = {"BANK_ACCOUNT", "UPI", "IFSC"}
    CONTACT_TYPES = {"PHONE", "EMAIL"}

    def calculate_risk(self, detections: List[Detection]) -> RiskCalculationResult:
        if not detections:
            return RiskCalculationResult(
                score=0.0,
                level="LOW",
                explanation="No sensitive information detected. This document passed current PRIVASCOPE detection policies.",
                breakdown={"raw_score": 0.0, "combination_multiplier": 1.0, "entity_counts": {}}
            )

        entity_counts: Dict[str, int] = {}
        for d in detections:
            entity_counts[d.entity_type] = entity_counts.get(d.entity_type, 0) + 1

        # Calculate individual entity risk contributions
        raw_score = 0.0
        itemized_breakdown = []
        
        for d in detections:
            base_sev = self.SEVERITY_WEIGHTS.get(d.entity_type, 4.0)
            conf = d.confidence
            
            # Context multiplier: if context signal exists, higher confidence
            has_context = "context" in d.detection_source
            context_mult = 1.20 if has_context else 1.00
            
            entity_risk = base_sev * conf * context_mult
            raw_score += entity_risk
            
            itemized_breakdown.append({
                "type": d.entity_type,
                "base_severity": base_sev,
                "confidence": conf,
                "context_multiplier": context_mult,
                "contribution": round(entity_risk, 2)
            })

        # Evaluate Combination Effects (Identity + Financial + Contact)
        present_types = set(d.entity_type for d in detections)
        has_identity = bool(present_types.intersection(self.IDENTITY_TYPES))
        has_financial = bool(present_types.intersection(self.FINANCIAL_TYPES))
        has_contact = bool(present_types.intersection(self.CONTACT_TYPES))

        combination_multiplier = 1.0
        combination_reasons = []

        if has_identity and has_financial and has_contact:
            combination_multiplier = 1.35
            combination_reasons.append("Triad exposure: Direct Identity + Financial Accounts + Contact coordinates present simultaneously")
        elif has_identity and has_financial:
            combination_multiplier = 1.25
            combination_reasons.append("Compounded exposure: Identity and Financial identifiers present together")
        elif has_identity and has_contact:
            combination_multiplier = 1.15
            combination_reasons.append("Compounded exposure: Identity and Direct Contact identifiers present together")

        # Multi-record exposure penalty (spreadsheets or lists with many individuals)
        if len(detections) > 10:
            scale_factor = min(1.25, 1.0 + (len(detections) / 100.0))
            combination_multiplier *= scale_factor
            combination_reasons.append(f"High-density volume exposure: {len(detections)} distinct sensitive records detected")

        final_raw = raw_score * combination_multiplier
        
        # Normalize into 0 - 100 scale using smooth saturation curve
        # A single critical Aadhaar + phone (approx 15-20 raw) gives ~60-70; multiple records reach 85-98
        normalized_score = min(100.0, max(0.0, (final_raw / (final_raw + 25.0)) * 100.0))
        normalized_score = round(normalized_score, 1)

        # Categorize risk level
        if normalized_score >= 81.0:
            level = "CRITICAL"
        elif normalized_score >= 61.0:
            level = "HIGH"
        elif normalized_score >= 31.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Generate transparent factual explanation
        type_names = sorted(list(present_types))
        explanation_parts = [
            f"This document contains {len(detections)} sensitive entities across {len(type_names)} categories: {', '.join(type_names)}."
        ]
        if combination_reasons:
            explanation_parts.append(" ".join(combination_reasons) + ".")
        
        if level in ("CRITICAL", "HIGH"):
            explanation_parts.append("Immediate redaction or masking is strongly recommended before sharing this document.")
        else:
            explanation_parts.append("Review detected items and apply masking if sharing beyond trusted parties.")
            
        explanation_parts.append(f"Note: {self.POLICY_DISCLAIMER}")
        explanation = " ".join(explanation_parts)

        return RiskCalculationResult(
            score=normalized_score,
            level=level,
            explanation=explanation,
            breakdown={
                "raw_score": round(raw_score, 2),
                "combination_multiplier": round(combination_multiplier, 2),
                "combination_reasons": combination_reasons,
                "entity_counts": entity_counts,
                "itemized_sample": itemized_breakdown[:10]
            }
        )

risk_engine = RiskEngine()
