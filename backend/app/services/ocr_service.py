import importlib.util
from pathlib import Path
from typing import Tuple, List, Optional
from app.processors.base import ContentBlock
from app.core.logger import logger

class OCRService:
    def __init__(self):
        self._easyocr_reader = None
        self._status_cache: Optional[str] = None

    @property
    def status(self) -> str:
        """Lazily determines OCR availability without eager ML model loading."""
        if self._status_cache is None:
            self._status_cache = self._check_ocr_availability()
        return self._status_cache

    def _check_ocr_availability(self) -> str:
        """Non-blocking inspection of available OCR backends without loading PyTorch weights."""
        if importlib.util.find_spec("pytesseract") is not None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                return "OCR_READY"
            except Exception:
                pass

        if importlib.util.find_spec("easyocr") is not None:
            return "OCR_READY"

        return "OCR_UNAVAILABLE"

    def _get_easyocr_reader(self):
        if self._easyocr_reader is None:
            try:
                import easyocr
                # Initialize English reader on CPU lazily only when requested
                self._easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            except Exception as e:
                logger.warning(f"Could not initialize EasyOCR reader: {e}")
                self._easyocr_reader = None
        return self._easyocr_reader

    def ocr_image(self, image_path: Path, page_num: int = 1) -> Tuple[str, List[ContentBlock], str]:
        """
        Runs OCR on an image file using available lightweight engine.
        Returns (full_text, content_blocks_with_bboxes, ocr_status).
        Never fakes coordinates or stages.
        """
        # 1. Try lightweight Tesseract OCR first (minimal RAM footprint)
        if importlib.util.find_spec("pytesseract") is not None:
            try:
                import pytesseract
                from PIL import Image

                with Image.open(image_path) as img:
                    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

                blocks: List[ContentBlock] = []
                text_lines: List[str] = []
                n_boxes = len(data.get("text", []))

                for i in range(n_boxes):
                    word = data["text"][i].strip()
                    conf = float(data.get("conf", [0])[i])
                    if word and conf > 0:
                        x = float(data["left"][i])
                        y = float(data["top"][i])
                        w = float(data["width"][i])
                        h = float(data["height"][i])
                        text_lines.append(word)
                        blocks.append(ContentBlock(
                            text=word,
                            page=page_num,
                            bbox=(x, y, w, h),
                            source="ocr",
                            context_meta={"ocr_confidence": conf / 100.0}
                        ))

                full_text = " ".join(text_lines)
                if full_text:
                    return full_text, blocks, "OCR_COMPLETED"
            except Exception as e:
                logger.debug(f"Pytesseract execution not available: {e}")

        # 2. Try EasyOCR lazily if installed
        if importlib.util.find_spec("easyocr") is not None:
            reader = self._get_easyocr_reader()
            if reader is not None:
                try:
                    results = reader.readtext(str(image_path))
                    blocks: List[ContentBlock] = []
                    text_lines: List[str] = []

                    for bbox, text, conf in results:
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
                    logger.warning(f"EasyOCR processing failed for {image_path.name}: {e}")
                    return "", [], "OCR_FAILED"

        return "", [], "OCR_UNAVAILABLE"

ocr_service = OCRService()

