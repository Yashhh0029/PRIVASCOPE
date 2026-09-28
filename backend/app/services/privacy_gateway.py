import time
import json
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.processors.base import ExtractedContent, ContentBlock
from app.detectors import ALL_DETECTORS, Detection, DetectionContext
from app.services.risk_engine import risk_engine
from app.services.policy_engine import policy_engine, PolicyDecision
from app.services.pseudonymization_service import pseudonymization_service
from app.services.providers import get_provider, BaseAIProvider
from app.models.gateway import GatewayAuditLog
from app.models.user import User

class GatewayResult:
    def __init__(
        self,
        session_id: str,
        policy_decision: str,
        policy_reasons: List[str],
        risk_score: float,
        risk_level: str,
        entities_detected: List[Dict[str, Any]],
        original_prompt_preview: str,
        protected_prompt: Optional[str],
        provider_received_prompt: Optional[str],
        provider_name: str,
        provider_display_name: str,
        provider_is_demo: bool,
        provider_raw_response: Optional[str],
        rehydrated_response: Optional[str],
        latencies_ms: Dict[str, float],
        exposure_summary: Dict[str, Any]
    ):
        self.session_id = session_id
        self.policy_decision = policy_decision
        self.policy_reasons = policy_reasons
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.entities_detected = entities_detected
        self.original_prompt_preview = original_prompt_preview
        self.protected_prompt = protected_prompt
        self.provider_received_prompt = provider_received_prompt
        self.provider_name = provider_name
        self.provider_display_name = provider_display_name
        self.provider_is_demo = provider_is_demo
        self.provider_raw_response = provider_raw_response
        self.rehydrated_response = rehydrated_response
        self.latencies_ms = latencies_ms
        self.exposure_summary = exposure_summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "policy_decision": self.policy_decision,
            "policy_reasons": self.policy_reasons,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "entities_detected": self.entities_detected,
            "original_prompt_preview": self.original_prompt_preview,
            "protected_prompt": self.protected_prompt,
            "provider_received_prompt": self.provider_received_prompt,
            "provider_name": self.provider_name,
            "provider_display_name": self.provider_display_name,
            "provider_is_demo": self.provider_is_demo,
            "provider_raw_response": self.provider_raw_response,
            "rehydrated_response": self.rehydrated_response,
            "latencies_ms": self.latencies_ms,
            "exposure_summary": self.exposure_summary
        }

class PrivacyGateway:
    def process_prompt(
        self,
        db: Session,
        user: User,
        prompt: str,
        provider_name: str = "local_demo",
        session_id: Optional[str] = None
    ) -> GatewayResult:
        """
        Executes end-to-end AI Privacy Firewall workflow.
        Guarantees that when policy is PROTECT, external providers NEVER receive raw PII.
        Guarantees that when policy is BLOCK, external providers are NEVER called.
        """
        t_start_total = time.perf_counter()
        
        if not session_id:
            session_id = f"gw_{uuid.uuid4().hex[:16]}"

        # Step 1: Detect PII across prompt text
        t_detect_start = time.perf_counter()
        content = ExtractedContent(raw_text=prompt, blocks=[ContentBlock(text=prompt, source="text")])
        ctx = DetectionContext(text_window_size=60)
        
        raw_detections: List[Detection] = []
        for det in ALL_DETECTORS:
            raw_detections.extend(det.detect(content, ctx))
            
        # Deduplicate overlapping matches
        deduped: dict[tuple[int, int, str], Detection] = {}
        for d in raw_detections:
            key = (d.block_index, d.start, d.entity_type)
            if key not in deduped or d.confidence > deduped[key].confidence:
                deduped[key] = d
        final_detections = list(deduped.values())
        t_detect_end = time.perf_counter()
        detection_latency_ms = round((t_detect_end - t_detect_start) * 1000.0, 2)

        # Step 2: Risk Calculation
        risk_result = risk_engine.calculate_risk(final_detections)

        # Step 3: Privacy Policy Evaluation
        t_policy_start = time.perf_counter()
        decision, reasons = policy_engine.evaluate_policy(final_detections, risk_result)
        t_policy_end = time.perf_counter()
        policy_latency_ms = round((t_policy_end - t_policy_start) * 1000.0, 2)

        tokenization_latency_ms = 0.0
        provider_latency_ms = 0.0
        protected_prompt = None
        provider_received_prompt = None
        provider_raw_response = None
        rehydrated_response = None
        
        provider = get_provider(provider_name)
        
        # Step 4: Decision Execution
        if decision == PolicyDecision.BLOCK:
            # PROVIDER IS NEVER CALLED
            provider_received_prompt = None
            provider_raw_response = None
            rehydrated_response = None
            sensitive_transmitted = 0
            protection_applied = False
            
        elif decision == PolicyDecision.PROTECT:
            # Reversible Local Pseudonymization
            t_tok_start = time.perf_counter()
            protected_prompt, applied_tokens = pseudonymization_service.pseudonymize(
                prompt,
                final_detections,
                session_id
            )
            t_tok_end = time.perf_counter()
            tokenization_latency_ms = round((t_tok_end - t_tok_start) * 1000.0, 2)
            
            # Send protected payload to provider
            t_prov_start = time.perf_counter()
            provider_received_prompt = protected_prompt
            provider_raw_response = provider.generate_response(protected_prompt)
            t_prov_end = time.perf_counter()
            provider_latency_ms = round((t_prov_end - t_prov_start) * 1000.0, 2)
            
            # Local Rehydration of tokens for user display
            rehydrated_response = pseudonymization_service.rehydrate(provider_raw_response, session_id)
            sensitive_transmitted = 0
            protection_applied = True
            
        else: # ALLOW or WARN
            protected_prompt = prompt
            provider_received_prompt = prompt
            t_prov_start = time.perf_counter()
            provider_raw_response = provider.generate_response(prompt)
            t_prov_end = time.perf_counter()
            provider_latency_ms = round((t_prov_end - t_prov_start) * 1000.0, 2)
            rehydrated_response = provider_raw_response
            sensitive_transmitted = len(final_detections)
            protection_applied = False

        t_total_end = time.perf_counter()
        total_latency_ms = round((t_total_end - t_start_total) * 1000.0, 2)

        # Step 5: Audit Log Persistence (Zero raw PII and zero raw prompt stored)
        entity_types = [d.entity_type for d in final_detections]
        audit_entry = GatewayAuditLog(
            user_id=user.id,
            session_id=session_id,
            provider=provider.name,
            policy_decision=decision,
            risk_score=risk_result.score,
            entities_detected_count=len(final_detections),
            entity_types_json=json.dumps(entity_types),
            detection_latency_ms=detection_latency_ms,
            policy_latency_ms=policy_latency_ms,
            tokenization_latency_ms=tokenization_latency_ms,
            provider_latency_ms=provider_latency_ms,
            total_latency_ms=total_latency_ms
        )
        db.add(audit_entry)
        db.commit()

        # Step 6: Format Telemetry
        entities_data = [
            {
                "entity_type": d.entity_type,
                "masked_preview": d.masked_preview,
                "confidence": d.confidence,
                "risk_level": d.risk_level,
                "context_signals": d.context_signals
            }
            for d in final_detections
        ]

        exposure_summary = {
            "sensitive_values_detected": len(final_detections),
            "sensitive_values_transmitted_externally": sensitive_transmitted,
            "protection_applied": protection_applied,
            "tokens_mapped_count": pseudonymization_service.get_token_count_for_session(session_id)
        }

        latencies_ms = {
            "detection_ms": detection_latency_ms,
            "policy_ms": policy_latency_ms,
            "tokenization_ms": tokenization_latency_ms,
            "provider_ms": provider_latency_ms,
            "total_ms": total_latency_ms
        }

        # Truncate prompt preview for privacy
        orig_preview = prompt if len(prompt) <= 120 else prompt[:117] + "..."

        return GatewayResult(
            session_id=session_id,
            policy_decision=decision,
            policy_reasons=reasons,
            risk_score=risk_result.score,
            risk_level=risk_result.level,
            entities_detected=entities_data,
            original_prompt_preview=orig_preview,
            protected_prompt=protected_prompt,
            provider_received_prompt=provider_received_prompt,
            provider_name=provider.name,
            provider_display_name=provider.display_name,
            provider_is_demo=provider.is_demo,
            provider_raw_response=provider_raw_response,
            rehydrated_response=rehydrated_response,
            latencies_ms=latencies_ms,
            exposure_summary=exposure_summary
        )

privacy_gateway = PrivacyGateway()
