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
        Runs high-speed, high-accuracy Tesseract OCR on an image file.
        Optimized for mobile payment receipts, IDs, and documents:
        - Downscales oversized images for 3x-5x faster OCR processing without loss of text fidelity
        - Preprocesses to grayscale for optimal Tesseract contrast
        - Groups OCR tokens into coherent line-level blocks so detectors have surrounding context
        """
        if self.status != "OCR_READY":
            logger.info(f"OCR not available for {image_path.name}; returning empty extraction.")
            return "", [], "OCR_UNAVAILABLE"

        try:
            import pytesseract
            from PIL import Image

            with Image.open(image_path) as img:
                orig_w, orig_h = img.size
                
                # 1. High-speed downscaling for oversized mobile screenshots (e.g. 1080x2400)
                max_dim = 1600
                scale = 1.0
                if max(orig_w, orig_h) > max_dim:
                    scale = max_dim / float(max(orig_w, orig_h))
                    new_w = max(1, int(orig_w * scale))
                    new_h = max(1, int(orig_h * scale))
                    ocr_img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                else:
                    ocr_img = img.copy()

                # 2. Convert to grayscale for faster processing & sharp contrast
                if ocr_img.mode not in ("L", "RGB"):
                    ocr_img = ocr_img.convert("RGB")
                gray_img = ocr_img.convert("L")

                # 3. Execute Tesseract with fast LSTM engine
                custom_config = r'--oem 1 --psm 3'
                data = pytesseract.image_to_data(gray_img, config=custom_config, output_type=pytesseract.Output.DICT)

            n_boxes = len(data.get("text", []))
            
            # 4. Group words into coherent lines for rich semantic context
            lines_map = {}
            word_blocks: List[ContentBlock] = []

            for i in range(n_boxes):
                raw_word = str(data["text"][i]).strip()
                conf_val = data.get("conf", [0])[i]
                try:
                    conf = float(conf_val)
                except (ValueError, TypeError):
                    conf = 0.0

                if raw_word and conf > 0:
                    # Rescale coordinates back to original image dimensions
                    x = float(data["left"][i]) / scale
                    y = float(data["top"][i]) / scale
                    w = float(data["width"][i]) / scale
                    h = float(data["height"][i]) / scale

                    word_info = {
                        "word": raw_word,
                        "conf": conf,
                        "bbox": (x, y, w, h)
                    }

                    # Group key: (block_num, par_num, line_num)
                    line_key = (
                        int(data.get("block_num", [0])[i]),
                        int(data.get("par_num", [0])[i]),
                        int(data.get("line_num", [0])[i])
                    )
                    if line_key not in lines_map:
                        lines_map[line_key] = []
                    lines_map[line_key].append(word_info)

                    # Also keep word-level block for precise single-token highlight
                    word_blocks.append(ContentBlock(
                        text=raw_word,
                        page=page_num,
                        bbox=(x, y, w, h),
                        source="ocr_word",
                        context_meta={"ocr_confidence": conf / 100.0}
                    ))

            # Assemble line blocks (provides surrounding context like "UTR:", "UPI ID:", "Phone:")
            line_blocks: List[ContentBlock] = []
            full_lines: List[str] = []

            for line_key, words in lines_map.items():
                line_text = " ".join(w["word"] for w in words)
                full_lines.append(line_text)
                min_x = min(w["bbox"][0] for w in words)
                min_y = min(w["bbox"][1] for w in words)
                max_x = max(w["bbox"][0] + w["bbox"][2] for w in words)
                max_y = max(w["bbox"][1] + w["bbox"][3] for w in words)
                avg_conf = sum(w["conf"] for w in words) / max(1, len(words))

                line_blocks.append(ContentBlock(
                    text=line_text,
                    page=page_num,
                    bbox=(min_x, min_y, max(1.0, max_x - min_x), max(1.0, max_y - min_y)),
                    source="ocr_line",
                    context_meta={"ocr_confidence": avg_conf / 100.0}
                ))

            # Combined content blocks: line blocks first (for context), followed by word blocks
            combined_blocks = line_blocks + word_blocks
            full_text = "\n".join(full_lines)
            return full_text, combined_blocks, "OCR_COMPLETED"
        except Exception as e:
            logger.error(f"Tesseract OCR processing failed for {image_path.name}: {e}")
            return "", [], "OCR_FAILED"


ocr_service = OCRService()
