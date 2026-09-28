from pathlib import Path
from typing import Optional
from app.processors.base import BaseProcessor, ExtractedContent, ContentBlock
from app.processors.txt_processor import TxtProcessor
from app.processors.csv_processor import CsvProcessor
from app.processors.excel_processor import ExcelProcessor
from app.processors.docx_processor import DocxProcessor
from app.processors.pdf_processor import PdfProcessor
from app.processors.image_processor import ImageProcessor

PROCESSOR_MAP = {
    "txt": TxtProcessor(),
    "csv": CsvProcessor(),
    "xlsx": ExcelProcessor(),
    "docx": DocxProcessor(),
    "pdf": PdfProcessor(),
    "png": ImageProcessor(),
    "jpg": ImageProcessor(),
    "jpeg": ImageProcessor(),
}

def get_processor_for_file(file_path: Path | str) -> Optional[BaseProcessor]:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")
    return PROCESSOR_MAP.get(ext)

__all__ = [
    "BaseProcessor",
    "ExtractedContent",
    "ContentBlock",
    "TxtProcessor",
    "CsvProcessor",
    "ExcelProcessor",
    "DocxProcessor",
    "PdfProcessor",
    "ImageProcessor",
    "get_processor_for_file"
]
