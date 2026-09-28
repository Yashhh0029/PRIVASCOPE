from pathlib import Path
from typing import List
from app.processors.base import BaseProcessor, ExtractedContent, ContentBlock

class TxtProcessor(BaseProcessor):
    format = "txt"

    def extract(self, file_path: Path) -> ExtractedContent:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        blocks: List[ContentBlock] = []
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if line.strip():
                blocks.append(ContentBlock(
                    text=line,
                    page=1,
                    source="txt",
                    row=idx + 1
                ))

        return ExtractedContent(
            raw_text=content,
            blocks=blocks,
            format=self.format,
            metadata={"line_count": len(lines)}
        )

    def protect(self, file_path: Path, output_path: Path, detections: list, mode: str) -> bool:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Sort detections by matched value length descending to avoid partial substring collisions
        sorted_detections = sorted(detections, key=lambda d: len(d.matched_value), reverse=True)

        for d in sorted_detections:
            replacement = "[REDACTED]" if mode == "REDACT" else d.masked_preview
            content = content.replace(d.matched_value, replacement)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    def verify_protection(self, output_path: Path, original_values: list[str]) -> bool:
        """Verifies that none of the original sensitive values can be read from the output file."""
        if not output_path.exists():
            return False
        with open(output_path, "r", encoding="utf-8", errors="replace") as f:
            protected_text = f.read()

        for val in original_values:
            if val and val in protected_text:
                return False
        return True
