import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.detectors import AadhaarDetector, UpiDetector, EmailDetector, PhoneDetector, DetectionContext
from app.processors.base import ExtractedContent, ContentBlock

def test_payment_receipt_accuracy():
    ctx = DetectionContext()
    
    # Simulated text extracted from a real PhonePe / GPay / Paytm payment receipt
    receipt_text = (
        "PhonePe Payment Success Receipt\n"
        "Paid to Rajesh Kumar\n"
        "UPI ID: 9876543210@ybl\n"
        "UTR: 429812345678\n"
        "Debited from A/c XX1234\n"
        "Mobile Number: +91 98765 43210\n"
        "Support: support@phonepe.com\n"
    )
    
    blocks = [
        ContentBlock(text="PhonePe Payment Success Receipt", page=1),
        ContentBlock(text="Paid to Rajesh Kumar", page=1),
        ContentBlock(text="UPI ID: 9876543210@ybl", page=1),
        ContentBlock(text="UTR: 429812345678", page=1),
        ContentBlock(text="Debited from A/c XX1234", page=1),
        ContentBlock(text="Mobile Number: +91 98765 43210", page=1),
        ContentBlock(text="Support: support@phonepe.com", page=1),
    ]
    
    content = ExtractedContent(raw_text=receipt_text, blocks=blocks, format="image")
    
    # 1. Aadhaar detector must NOT flag the 12-digit UTR as Aadhaar
    aadhaar_detections = AadhaarDetector().detect(content, ctx)
    assert len(aadhaar_detections) == 0, f"False positive: UTR was flagged as Aadhaar: {aadhaar_detections}"
    
    # 2. UPI detector must detect 9876543210@ybl
    upi_detections = UpiDetector().detect(content, ctx)
    assert len(upi_detections) == 1, f"Expected 1 UPI detection, got {len(upi_detections)}"
    assert upi_detections[0].matched_value == "9876543210@ybl"
    
    # 3. Email detector must NOT flag support@phonepe.com as personal PII
    email_detections = EmailDetector().detect(content, ctx)
    assert len(email_detections) == 0, f"False positive: support email was flagged as personal PII: {email_detections}"
    
    # 4. Phone detector must detect mobile numbers (+91 98765 43210 or in UPI)
    phone_detections = PhoneDetector().detect(content, ctx)
    assert len(phone_detections) >= 1, f"Expected at least 1 phone detection, got {len(phone_detections)}"
    
    print("test_payment_receipt_accuracy: PASSED")

def test_real_aadhaar_with_verhoeff():
    ctx = DetectionContext()
    valid_uid = "234567890124" # Passes Verhoeff algorithm
    content = ExtractedContent(
        raw_text=f"Resident Aadhaar: {valid_uid}",
        blocks=[ContentBlock(text=f"Aadhaar Number: {valid_uid}", page=1)],
        format="image"
    )
    detections = AadhaarDetector().detect(content, ctx)
    assert len(detections) == 1, "Real Aadhaar number with Verhoeff should be detected"
    print("test_real_aadhaar_with_verhoeff: PASSED")

if __name__ == "__main__":
    test_payment_receipt_accuracy()
    test_real_aadhaar_with_verhoeff()
    print("ALL ACCURACY TESTS PASSED!")
