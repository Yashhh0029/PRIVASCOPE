import os
import shutil
import importlib.util
from pathlib import Path
from typing import Tuple, List, Optional
from app.processors.base import ContentBlock
from app.core.logger import logger


class OCRService:
    def __init__(self):
        self._binary_path: Optional[Path] = None
        self._tesseract_configured: bool = False
        self._status_cache: Optional[str] = None

    def _discover_and_configure_tesseract(self) -> Optional[Path]:
        """Discovers the Tesseract binary across standard system paths and configures pytesseract."""
        if self._tesseract_configured and self._binary_path and self._binary_path.exists():
            return self._binary_path

        # 1. Check system PATH
        candidate = shutil.which("tesseract") or shutil.which("tesseract.exe")
        if candidate:
            p = Path(candidate)
            if p.is_file():
                self._binary_path = p

        # 2. Check standard Linux/Debian locations (including non-root Render installations)
        if not self._binary_path:
            linux_candidates = [
                Path.home() / ".local" / "usr" / "bin" / "tesseract",
                Path("/usr/bin/tesseract"),
                Path("/usr/local/bin/tesseract"),
                Path("/usr/bin/tesseract-ocr"),
            ]
            for lp in linux_candidates:
                if lp.is_file():
                    self._binary_path = lp
                    break

        # 3. Check standard Windows locations
        if not self._binary_path:
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

            win_candidates = [
                Path(prog_files) / "Tesseract-OCR" / "tesseract.exe",
                Path(prog_files_x86) / "Tesseract-OCR" / "tesseract.exe",
                Path(local_app_data) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            ]
            for wp in win_candidates:
                if wp.is_file():
                    self._binary_path = wp
                    break

        # 4. If binary found, configure pytesseract and tessdata paths
        if self._binary_path and self._binary_path.exists():
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = str(self._binary_path)

                # Set TESSDATA_PREFIX if not already set and standard directory exists
                if "TESSDATA_PREFIX" not in os.environ:
                    tessdata_candidates = [
                        Path.home() / ".local" / "usr" / "share" / "tesseract-ocr" / "5" / "tessdata",
                        Path.home() / ".local" / "usr" / "share" / "tesseract-ocr" / "4.00" / "tessdata",
                        Path("/usr/share/tesseract-ocr/5/tessdata"),
                        Path("/usr/share/tesseract-ocr/4.00/tessdata"),
                        self._binary_path.parent / "tessdata",
                    ]
                    for td in tessdata_candidates:
                        if td.is_dir():
                            os.environ["TESSDATA_PREFIX"] = str(td)
                            break

                self._tesseract_configured = True
                return self._binary_path
            except Exception as e:
                logger.warning(f"Error configuring pytesseract with binary {self._binary_path}: {e}")
                return None

        return None

    @property
    def status(self) -> str:
        """Dynamically determines OCR availability without eager ML imports or crashes."""
        if self._status_cache is None:
            self._status_cache = self._check_ocr_availability()
        return self._status_cache

    def _check_ocr_availability(self) -> str:
        """Verifies if pytesseract module and Tesseract binary are functional."""
        if importlib.util.find_spec("pytesseract") is None:
            return "OCR_UNAVAILABLE"

        bin_path = self._discover_and_configure_tesseract()
        if not bin_path:
            return "OCR_UNAVAILABLE"

        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR verified ready (v{version}) at {bin_path}")
            return "OCR_READY"
        except Exception as e:
            logger.debug(f"Tesseract OCR check failed: {e}")
            return "OCR_UNAVAILABLE"

    def ocr_image(self, image_path: Path, page_num: int = 1) -> Tuple[str, List[ContentBlock], str]:
        """
        Runs native Tesseract OCR on an image file.
        Returns (full_text, content_blocks_with_bboxes, ocr_status).
        Truthful reporting only: OCR_COMPLETED, OCR_FAILED, or OCR_UNAVAILABLE.
        """
        if self.status != "OCR_READY":
            logger.info(f"OCR not available for {image_path.name}; returning empty extraction.")
            return "", [], "OCR_UNAVAILABLE"

        try:
            import pytesseract
            from PIL import Image

            with Image.open(image_path) as img:
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            blocks: List[ContentBlock] = []
            text_lines: List[str] = []
            n_boxes = len(data.get("text", []))

            for i in range(n_boxes):
                word = str(data["text"][i]).strip()
                conf_val = data.get("conf", [0])[i]
                try:
                    conf = float(conf_val)
                except (ValueError, TypeError):
                    conf = 0.0

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
            return full_text, blocks, "OCR_COMPLETED"
        except Exception as e:
            logger.error(f"Tesseract OCR processing failed for {image_path.name}: {e}")
            return "", [], "OCR_FAILED"


ocr_service = OCRService()
