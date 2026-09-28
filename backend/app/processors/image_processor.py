from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFilter
from app.processors.base import BaseProcessor, ExtractedContent, ContentBlock
from app.core.logger import logger

class ImageProcessor(BaseProcessor):
    format = "image"

    def extract(self, file_path: Path) -> ExtractedContent:
        from app.services.ocr_service import ocr_service
        text, blocks, ocr_status = ocr_service.ocr_image(file_path, page_num=1)
        
        with Image.open(file_path) as img:
            width, height = img.size

        return ExtractedContent(
            raw_text=text,
            blocks=blocks,
            format=self.format,
            metadata={
                "width": width,
                "height": height,
                "ocr_status": ocr_status
            }
        )

    def protect(self, file_path: Path, output_path: Path, detections: list, mode: str) -> bool:
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            for d in detections:
                loc = d.location
                if not loc or not loc.get("bbox"):
                    continue

                bbox = loc["bbox"]  # (x, y, w, h)
                x, y, w, h = bbox
                # Add small padding to ensure complete coverage of text edges
                pad = 4
                x0 = max(0, int(x - pad))
                y0 = max(0, int(y - pad))
                x1 = min(img.width, int(x + w + pad))
                y1 = min(img.height, int(y + h + pad))

                if mode == "REDACT":
                    # Solid black rectangle covering the detected sensitive area
                    draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0))
                else:
                    # Mask mode: Blur or pixelate the region
                    region = img.crop((x0, y0, x1, y1))
                    blurred_region = region.filter(ImageFilter.GaussianBlur(radius=15))
                    img.paste(blurred_region, (x0, y0))

            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(output_path), quality=95)
        return True

    def verify_protection(self, output_path: Path, original_values: list[str]) -> bool:
        """Verifies that the output image exists and can be loaded as valid image data."""
        if not output_path.exists():
            return False
        try:
            with Image.open(output_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Image protection verification failed: {e}")
            return False
