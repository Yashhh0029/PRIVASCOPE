import io
import zipfile
from pathlib import Path
from typing import Tuple, Optional

# Magic byte signatures
SIGNATURE_PDF = b"%PDF-"
SIGNATURE_PNG = b"\x89PNG\r\n\x1a\n"
SIGNATURE_JPEG = b"\xff\xd8\xff"
SIGNATURE_ZIP = b"PK\x03\x04"

class FileValidationError(Exception):
    """Raised when file content signature does not match its declared type or violates safety policy."""
    pass

def validate_file_signature(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validates the binary magic bytes of an uploaded file against its declared extension.
    Prevents extension spoofing (e.g. executable/malicious bytes renamed to .pdf or .jpg).
    Returns (is_valid: bool, detected_mime_or_error: str).
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    if not ext:
        raise FileValidationError("Uploaded file has no extension.")

    size = len(file_bytes)
    if size == 0:
        raise FileValidationError("File is empty (0 bytes).")

    if ext == "pdf":
        if not file_bytes.startswith(SIGNATURE_PDF):
            raise FileValidationError("File signature mismatch: declared as PDF but header is not '%PDF-'.")
        return True, "application/pdf"

    elif ext == "png":
        if not file_bytes.startswith(SIGNATURE_PNG):
            raise FileValidationError("File signature mismatch: declared as PNG but does not have valid PNG magic bytes.")
        return True, "image/png"

    elif ext in ("jpg", "jpeg"):
        if not file_bytes.startswith(SIGNATURE_JPEG):
            raise FileValidationError("File signature mismatch: declared as JPEG/JPG but does not have valid JPEG magic bytes.")
        return True, "image/jpeg"

    elif ext == "docx":
        if not file_bytes.startswith(SIGNATURE_ZIP):
            raise FileValidationError("File signature mismatch: declared as DOCX but lacks valid ZIP/Office container header.")
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                # Microsoft Word files must contain word/document.xml or [Content_Types].xml
                namelist = z.namelist()
                if not any(name.startswith("word/") for name in namelist) and "[Content_Types].xml" not in namelist:
                    raise FileValidationError("Invalid DOCX file: missing internal Word XML schema structure.")
        except zipfile.BadZipFile:
            raise FileValidationError("Corrupt or invalid DOCX archive file.")
        return True, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    elif ext == "xlsx":
        if not file_bytes.startswith(SIGNATURE_ZIP):
            raise FileValidationError("File signature mismatch: declared as XLSX but lacks valid ZIP/Office container header.")
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                # Microsoft Excel files must contain xl/workbook.xml or [Content_Types].xml
                namelist = z.namelist()
                if not any(name.startswith("xl/") for name in namelist) and "[Content_Types].xml" not in namelist:
                    raise FileValidationError("Invalid XLSX file: missing internal Excel XML schema structure.")
        except zipfile.BadZipFile:
            raise FileValidationError("Corrupt or invalid XLSX archive file.")
        return True, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    elif ext in ("csv", "txt"):
        # Plain text must not contain binary null bytes (\x00)
        if b"\x00" in file_bytes[:1024]:
            raise FileValidationError(f"File declared as {ext.upper()} contains binary null bytes; cannot be plain text.")
        try:
            file_bytes[:4096].decode("utf-8")
        except UnicodeDecodeError:
            raise FileValidationError(f"File declared as {ext.upper()} is not valid UTF-8 text.")
        return True, "text/csv" if ext == "csv" else "text/plain"

    else:
        raise FileValidationError(f"Unsupported file format extension: .{ext}")
