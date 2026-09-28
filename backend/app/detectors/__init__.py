from app.detectors.base import BaseDetector, Detection, DetectionContext
from app.detectors.aadhaar import AadhaarDetector
from app.detectors.pan import PanDetector
from app.detectors.phone import PhoneDetector
from app.detectors.email import EmailDetector
from app.detectors.upi import UpiDetector
from app.detectors.ifsc import IfscDetector
from app.detectors.bank_account import BankAccountDetector
from app.detectors.student_id import StudentIdDetector

ALL_DETECTORS = [
    AadhaarDetector(),
    PanDetector(),
    PhoneDetector(),
    EmailDetector(),
    UpiDetector(),
    IfscDetector(),
    BankAccountDetector(),
    StudentIdDetector(),
]

__all__ = [
    "BaseDetector",
    "Detection",
    "DetectionContext",
    "AadhaarDetector",
    "PanDetector",
    "PhoneDetector",
    "EmailDetector",
    "UpiDetector",
    "IfscDetector",
    "BankAccountDetector",
    "StudentIdDetector",
    "ALL_DETECTORS"
]
