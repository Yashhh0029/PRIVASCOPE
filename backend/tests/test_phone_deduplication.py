"""
Regression tests for PRIVASCOPE Phone Deduplication Pipeline.
Verifies that:
1. The same phone number across multiple document blocks yields exactly 1 finding.
2. The same phone number with formatting variations (+91, spaces, dashes) yields exactly 1 finding.
3. Different actual phone numbers remain separate findings.
4. The richest/highest-confidence detection is preserved during deduplication.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.detectors import ALL_DETECTORS, DetectionContext
from app.processors.base import ExtractedContent, ContentBlock
from app.services.scan_pipeline import normalize_entity_value


def run_pipeline_deduplication(blocks: list[ContentBlock]):
    """Simulates detector execution + Stage 5 deduplication from ScanPipeline."""
    content = ExtractedContent(
        raw_text="\n".join(b.text for b in blocks),
        blocks=blocks,
        format="txt"
    )
    det_context = DetectionContext(text_window_size=60)
    all_detections = []
    for detector in ALL_DETECTORS:
        all_detections.extend(detector.detect(content, det_context))

    deduped = {}
    for d in all_detections:
        norm_val = normalize_entity_value(d.entity_type, d.matched_value)
        key = (d.entity_type, norm_val)
        if key not in deduped:
            deduped[key] = d
        else:
            existing = deduped[key]
            new_score = (d.confidence, len(d.detection_source), len(d.matched_value))
            existing_score = (existing.confidence, len(existing.detection_source), len(existing.matched_value))
            if new_score > existing_score:
                deduped[key] = d

    return list(deduped.values())


def test_same_phone_in_different_blocks_yields_one_finding():
    blocks = [
        ContentBlock(text="Header Contact: 9876543210", page=1, source="text"),
        ContentBlock(text="Body: Call me at 9876543210 for queries", page=1, source="text"),
    ]
    detections = run_pipeline_deduplication(blocks)
    phone_detections = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phone_detections) == 1, f"Expected 1 PHONE finding, got {len(phone_detections)}"
    assert normalize_entity_value("PHONE", phone_detections[0].matched_value) == "9876543210"


def test_same_phone_with_formatting_differences_yields_one_finding():
    blocks = [
        ContentBlock(text="Primary: +91 9876543210", page=1, source="text"),
        ContentBlock(text="Alternative: 9876543210", page=1, source="text"),
        ContentBlock(text="Direct: +91-9876543210", page=1, source="text"),
    ]
    detections = run_pipeline_deduplication(blocks)
    phone_detections = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phone_detections) == 1, f"Expected 1 PHONE finding for formatted variations, got {len(phone_detections)}"
    assert normalize_entity_value("PHONE", phone_detections[0].matched_value) == "9876543210"


def test_two_different_phones_yield_two_findings():
    blocks = [
        ContentBlock(text="Mobile 1: 9876543210", page=1, source="text"),
        ContentBlock(text="Mobile 2: 9123456780", page=1, source="text"),
    ]
    detections = run_pipeline_deduplication(blocks)
    phone_detections = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phone_detections) == 2, f"Expected 2 distinct PHONE findings, got {len(phone_detections)}"
    normalized_numbers = {normalize_entity_value("PHONE", d.matched_value) for d in phone_detections}
    assert normalized_numbers == {"9876543210", "9123456780"}


def test_preserves_strongest_richest_detection():
    # Block 1 has no positive phone keyword (confidence ~0.70, source=['regex'])
    # Block 2 has explicit 'Phone:' keyword (confidence 0.95, source=['regex', 'context'])
    blocks = [
        ContentBlock(text="9876543210", page=1, source="text"),
        ContentBlock(text="Phone: +91 9876543210", page=1, source="text"),
    ]
    detections = run_pipeline_deduplication(blocks)
    phone_detections = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phone_detections) == 1
    best = phone_detections[0]
    assert best.confidence >= 0.90
    assert "context" in best.detection_source


if __name__ == "__main__":
    test_same_phone_in_different_blocks_yields_one_finding()
    test_same_phone_with_formatting_differences_yields_one_finding()
    test_two_different_phones_yield_two_findings()
    test_preserves_strongest_richest_detection()
    print("ALL REGRESSION TESTS PASSED SUCCESSFULLY!")
