import re
import logging
import sys

# PII Regex patterns for log scrubbing
AADHAAR_REGEX = re.compile(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b')
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE)
PHONE_REGEX = re.compile(r'(?:\+91[\-\s]?)?[6789]\d{9}\b')
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
UPI_REGEX = re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b')
BANK_ACC_REGEX = re.compile(r'\b\d{9,18}\b')

def sanitize_text(text: str) -> str:
    """Sanitize any raw sensitive PII strings before writing to logs."""
    if not isinstance(text, str):
        text = str(text)
    
    # Sanitize Aadhaar
    text = AADHAAR_REGEX.sub("[AADHAAR_MASKED]", text)
    # Sanitize PAN
    text = PAN_REGEX.sub("[PAN_MASKED]", text)
    # Sanitize Phone
    text = PHONE_REGEX.sub("[PHONE_MASKED]", text)
    # Sanitize Email
    text = EMAIL_REGEX.sub("[EMAIL_MASKED]", text)
    # Sanitize UPI
    text = UPI_REGEX.sub("[UPI_MASKED]", text)
    
    return text

class PIISanitizingFormatter(logging.Formatter):
    """Custom logging formatter that strips raw PII from log records and stack traces."""
    def format(self, record: logging.LogRecord) -> str:
        original_msg = record.getMessage()
        sanitized_msg = sanitize_text(original_msg)
        record.msg = sanitized_msg
        record.args = ()
        
        formatted = super().format(record)
        return sanitize_text(formatted)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = PIISanitizingFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = get_logger("privascope")
