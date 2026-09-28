from pathlib import Path
from typing import Tuple, List, Optional
from app.processors.base import ContentBlock
from app.core.logger import logger

class OCRService:
    def __init__(self):
        self._easyocr_reader = None
        self._status = self._check_ocr_availability()

    def _check_ocr_availability(self) -> str:
        try:
            import easyocr
            return "OCR_READY"
        except Exception:
            try:
                import pytesseract
                return "OCR_READY"
            except Exception:
                return "OCR_UNAVAILABLE"

    @property
    def status(self) -> str:
        return self._status

    def _get_easyocr_reader(self):
        if self._easyocr_reader is None:
            try:
                import easyocr
                # Initialize English reader on CPU
                self._easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            except Exception as e:
                logger.warning(f"Could not initialize EasyOCR reader: {e}")
                self._status = "OCR_FAILED"
                self._easyocr_reader = None
        return self._easyocr_reader

    def ocr_image(self, image_path: Path, page_num: int = 1) -> Tuple[str, List[ContentBlock], str]:
        """
        Runs OCR on an image file.
        Returns (full_text, content_blocks_with_bboxes, ocr_status).
        Never fakes coordinates or stages.
        """
        reader = self._get_easyocr_reader()
        if reader is None:
            return "", [], "OCR_UNAVAILABLE"

        try:
            results = reader.readtext(str(image_path))
            blocks: List[ContentBlock] = []
            text_lines: List[str] = []

            for bbox, text, conf in results:
                # bbox is [[x0,y0], [x1,y0], [x1,y1], [x0,y1]]
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
                norm_bbox = (float(x_min), float(y_min), float(x_max - x_min), float(y_max - y_min))

                text_lines.append(text)
                blocks.append(ContentBlock(
                    text=text,
                    page=page_num,
                    bbox=norm_bbox,
                    source="ocr",
                    context_meta={"ocr_confidence": float(conf)}
                ))

            full_text = "\n".join(text_lines)
            return full_text, blocks, "OCR_COMPLETED"
        except Exception as e:
            logger.warning(f"OCR processing failed for {image_path.name}: {e}")
            return "", [], "OCR_FAILED"

ocr_service = OCRService()
