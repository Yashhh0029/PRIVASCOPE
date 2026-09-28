from pathlib import Path
from typing import List, Optional
import pymupdf as fitz
from app.processors.base import BaseProcessor, ExtractedContent, ContentBlock
from app.core.logger import logger

class PdfProcessor(BaseProcessor):
    format = "pdf"

    def extract(self, file_path: Path) -> ExtractedContent:
        doc = fitz.open(str(file_path))
        blocks: List[ContentBlock] = []
        raw_lines: List[str] = []
        ocr_performed = False

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            
            # Extract native text with word/block bounding boxes
            # get_text("blocks") returns (x0, y0, x1, y1, "text", block_no, block_type)
            page_blocks = page.get_text("blocks")
            has_native_text = False

            for b in page_blocks:
                b_text = b[4].strip()
                if b_text:
                    has_native_text = True
                    raw_lines.append(b_text)
                    bbox = (float(b[0]), float(b[1]), float(b[2] - b[0]), float(b[3] - b[1]))
                    blocks.append(ContentBlock(
                        text=b_text,
                        page=page_num,
                        bbox=bbox,
                        source="pdf"
                    ))

            # If page has no native text (scanned document), run layered OCR
            if not has_native_text:
                from app.services.ocr_service import ocr_service
                logger.info(f"Page {page_num} of {file_path.name} contains no digital text. Triggering OCR layer.")
                pix = page.get_pixmap(dpi=150)
                temp_img_path = file_path.parent / f"temp_page_{page_num}_{file_path.stem}.png"
                pix.save(str(temp_img_path))
                
                ocr_text, ocr_blocks, status = ocr_service.ocr_image(temp_img_path, page_num=page_num)
                if temp_img_path.exists():
                    temp_img_path.unlink()
                
                if ocr_text:
                    ocr_performed = True
                    raw_lines.append(ocr_text)
                    blocks.extend(ocr_blocks)

        page_count = len(doc)
        doc.close()
        return ExtractedContent(
            raw_text="\n".join(raw_lines),
            blocks=blocks,
            format=self.format,
            metadata={"pages": page_count, "ocr_used": ocr_performed}
        )

    def protect(self, file_path: Path, output_path: Path, detections: list, mode: str) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        """
        True PDF Redaction vs Visual Masking.
        Uses PyMuPDF's apply_redactions() to physically eliminate sensitive characters
        from the underlying PDF content stream.
        """
        doc = fitz.open(str(file_path))

        for d in detections:
            target_val = d.matched_value
            replacement = "[REDACTED]" if mode == "REDACT" else d.masked_preview

            # Search across all pages
            for page in doc:
                rects = page.search_for(target_val)
                for rect in rects:
                    if mode == "REDACT":
                        # Irreversible solid black block redaction (purges characters from PDF stream)
                        page.add_redact_annot(rect, fill=(0, 0, 0))
                    else:
                        # Mask mode: Replace sensitive content with masked preview text
                        page.add_redact_annot(rect, text=replacement, fill=(0.95, 0.95, 0.95), text_color=(0, 0, 0))

                page.apply_redactions()

        # Save to output path without garbage or retained incremental history
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()
        return True

    def verify_protection(self, output_path: Path, original_values: list[str]) -> bool:
        """
        Acceptance test: Re-extracts all text from protected PDF.
        Asserts that NONE of the original sensitive values exist in the content stream.
        """
        if not output_path.exists():
            return False

        try:
            doc = fitz.open(str(output_path))
            extracted_text = []
            for page in doc:
                extracted_text.append(page.get_text())
            doc.close()

            full_text = " ".join(extracted_text)
            for val in original_values:
                if val and val in full_text:
                    logger.warning(f"Verification failed: '{val}' still extractable from protected PDF")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error during PDF protection verification: {e}")
            return False

    def render_page_preview(self, file_path: Path, page_num: int = 1, output_png: Optional[Path] = None) -> Optional[bytes]:
        """Renders a PDF page to PNG for frontend preview and heatmap overlays."""
        try:
            doc = fitz.open(str(file_path))
            if page_num > len(doc) or page_num < 1:
                page_num = 1
            page = doc[page_num - 1]
            pix = page.get_pixmap(dpi=150)
            png_bytes = pix.tobytes("png")
            if output_png:
                pix.save(str(output_png))
            doc.close()
            return png_bytes
        except Exception as e:
            logger.warning(f"Failed to render preview for {file_path.name}: {e}")
            return None
