import time
import re
import threading
from typing import Dict, Tuple, List, Optional
from app.detectors.base import Detection
from app.core.logger import logger

class PseudonymizationSession:
    def __init__(self, session_id: str, ttl_seconds: int = 1800):
        self.session_id = session_id
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds
        # Mapping: token -> raw_sensitive_value (Local in-memory ONLY)
        self.token_to_raw: Dict[str, str] = {}
        # Mapping: raw_sensitive_value -> token
        self.raw_to_token: Dict[str, str] = {}
        # Counter per entity type to generate <TYPE_01>, <TYPE_02>
        self.type_counters: Dict[str, int] = {}

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def get_or_create_token(self, entity_type: str, raw_value: str) -> str:
        clean_raw = raw_value.strip()
        if clean_raw in self.raw_to_token:
            return self.raw_to_token[clean_raw]

        counter = self.type_counters.get(entity_type, 0) + 1
        self.type_counters[entity_type] = counter
        token = f"<{entity_type}_{counter:02d}>"

        self.raw_to_token[clean_raw] = token
        self.token_to_raw[token] = clean_raw
        return token

    def rehydrate(self, text: str) -> str:
        """Locally replaces tokens with their original sensitive values."""
        if not text:
            return text
        result = text
        for token, raw_val in self.token_to_raw.items():
            result = result.replace(token, raw_val)
        return result

class PseudonymizationService:
    def __init__(self, ttl_seconds: int = 1800):
        self._sessions: Dict[str, PseudonymizationSession] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds

    def _cleanup_expired(self):
        """Thread-safe purge of expired sessions."""
        now = time.time()
        expired_keys = [sid for sid, s in self._sessions.items() if s.expires_at < now]
        for sid in expired_keys:
            del self._sessions[sid]

    def get_session(self, session_id: str) -> PseudonymizationSession:
        with self._lock:
            self._cleanup_expired()
            if session_id not in self._sessions:
                self._sessions[session_id] = PseudonymizationSession(session_id, self._ttl_seconds)
            return self._sessions[session_id]

    def pseudonymize(
        self,
        text: str,
        detections: List[Detection],
        session_id: str
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Replaces sensitive values in text with typed placeholder tokens (<TYPE_01>).
        Returns (protected_text, list_of_applied_tokens: [(token, entity_type)]).
        
        CRITICAL SECURITY GUARANTEE:
        The returned protected_text NEVER contains the original sensitive values.
        The token mapping is preserved strictly in local in-memory session cache.
        """
        session = self.get_session(session_id)
        
        # Sort detections in reverse order of start position to prevent index offset corruption
        sorted_dets = sorted(detections, key=lambda d: d.start, reverse=True)
        
        protected = text
        applied_tokens = []
        
        # Track replacements to ensure exact substitution
        for d in sorted_dets:
            token = session.get_or_create_token(d.entity_type, d.matched_value)
            applied_tokens.append((token, d.entity_type))
            
            # Precise position replacement if substring matches
            if d.start < len(protected) and d.end <= len(protected) and protected[d.start:d.end] == d.matched_value:
                protected = protected[:d.start] + token + protected[d.end:]
            else:
                # Fallback to direct string replacement
                protected = protected.replace(d.matched_value, token)

        return protected, applied_tokens

    def rehydrate(self, text: str, session_id: str) -> str:
        """
        Replaces placeholder tokens in text with the original sensitive values.
        This occurs EXCLUSIVELY on the user's local machine/backend for display.
        """
        with self._lock:
            self._cleanup_expired()
            session = self._sessions.get(session_id)
            if not session:
                logger.warning(f"Rehydration attempted for unknown or expired session: {session_id}")
                return text
            return session.rehydrate(text)

    def get_token_count_for_session(self, session_id: str) -> int:
        with self._lock:
            session = self._sessions.get(session_id)
            return len(session.token_to_raw) if session else 0

pseudonymization_service = PseudonymizationService()
