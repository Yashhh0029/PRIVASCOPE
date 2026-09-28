from typing import List, Dict, Any, Tuple
from app.detectors.base import Detection
from app.services.risk_engine import RiskCalculationResult

class PolicyDecision:
    ALLOW = "ALLOW"
    WARN = "WARN"
    PROTECT = "PROTECT"
    BLOCK = "BLOCK"

class PrivacyPolicyEngine:
    """
    Evaluates privacy policy decisions for outbound prompts and documents.
    Policy decisions determine whether a payload can be transmitted as-is (ALLOW),
    with a warning (WARN), requires reversible pseudonymization (PROTECT),
    or must be halted entirely (BLOCK).
    """
    def __init__(
        self,
        block_threshold: float = 80.0,
        protect_threshold: float = 25.0,
        warn_threshold: float = 5.0
    ):
        self.block_threshold = block_threshold
        self.protect_threshold = protect_threshold
        self.warn_threshold = warn_threshold

    def evaluate_policy(
        self,
        detections: List[Detection],
        risk_result: RiskCalculationResult
    ) -> Tuple[str, List[str]]:
        reasons: List[str] = []
        score = risk_result.score

        if not detections or score == 0.0:
            reasons.append("No sensitive personal data detected; request permitted as-is.")
            return PolicyDecision.ALLOW, reasons

        present_types = sorted(list(set(d.entity_type for d in detections)))
        has_aadhaar = "AADHAAR" in present_types
        has_pan = "PAN" in present_types
        has_bank = "BANK_ACCOUNT" in present_types
        has_phone = "PHONE" in present_types

        # Rule 1: Compound Critical Triad or high saturation risk -> BLOCK
        # If Aadhaar + Financial + Phone or score >= block_threshold -> BLOCK
        if score >= self.block_threshold or (has_aadhaar and has_bank and has_phone):
            reasons.append(
                f"Critical combined exposure risk (Score: {score:.1f}/100 >= {self.block_threshold}). "
                "Co-occurrence of national identity and financial coordinates exceeds outbound safety threshold."
            )
            reasons.append("Outbound transmission prohibited to prevent total identity and financial account compromise.")
            return PolicyDecision.BLOCK, reasons

        # Rule 2: High or Medium sensitivity personal data -> PROTECT
        # Replaces raw values with reversible pseudonymized tokens before transmission
        if score >= self.protect_threshold or has_aadhaar or has_pan or has_bank or has_phone:
            reasons.append(
                f"Sensitive personal identifiers detected ({', '.join(present_types)}). "
                f"Calculated privacy risk: {score:.1f}/100."
            )
            reasons.append(
                "Protection policy active: sensitive values must be transformed into "
                "pseudonymized tokens (<TYPE_01>) prior to external transmission."
            )
            return PolicyDecision.PROTECT, reasons

        # Rule 3: Low-sensitivity isolated contact information -> WARN
        reasons.append(
            f"Low-sensitivity personal coordinate detected ({', '.join(present_types)}). "
            f"Calculated risk: {score:.1f}/100."
        )
        reasons.append("Permitted with privacy advisory warning.")
        return PolicyDecision.WARN, reasons

policy_engine = PrivacyPolicyEngine()
