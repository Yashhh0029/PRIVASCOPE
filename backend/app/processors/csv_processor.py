import csv
from pathlib import Path
from typing import List
from app.processors.base import BaseProcessor, ExtractedContent, ContentBlock

class CsvProcessor(BaseProcessor):
    format = "csv"

    def extract(self, file_path: Path) -> ExtractedContent:
        blocks: List[ContentBlock] = []
        raw_lines: List[str] = []

        with open(file_path, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f)
            header = None
            for row_idx, row in enumerate(reader):
                raw_lines.append(",".join(row))
                if row_idx == 0:
                    header = [h.strip() for h in row]
                    # Also include header in content blocks for context analysis
                    for col_idx, col_val in enumerate(row):
                        blocks.append(ContentBlock(
                            text=col_val,
                            page=1,
                            source="csv",
                            row=row_idx + 1,
                            col=col_idx + 1,
                            col_name="HEADER"
                        ))
                    continue

                for col_idx, cell_value in enumerate(row):
                    if not cell_value.strip():
                        continue
                    col_name = header[col_idx] if (header and col_idx < len(header)) else f"Col{col_idx+1}"
                    blocks.append(ContentBlock(
                        text=cell_value,
                        page=1,
                        source="csv",
                        row=row_idx + 1,
                        col=col_idx + 1,
                        col_name=col_name
                    ))

        return ExtractedContent(
            raw_text="\n".join(raw_lines),
            blocks=blocks,
            format=self.format,
            metadata={"row_count": len(raw_lines)}
        )

    def protect(self, file_path: Path, output_path: Path, detections: list, mode: str) -> bool:
        # Build mapping of values to their replacement
        val_map = {}
        for d in detections:
            replacement = "[REDACTED]" if mode == "REDACT" else d.masked_preview
            val_map[d.matched_value] = replacement

        with open(file_path, "r", encoding="utf-8", errors="replace", newline="") as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        protected_rows = []
        for row in rows:
            new_row = []
            for cell in row:
                modified_cell = cell
                for orig_val, repl in val_map.items():
                    if orig_val in modified_cell:
                        modified_cell = modified_cell.replace(orig_val, repl)
                new_row.append(modified_cell)
            protected_rows.append(new_row)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerows(protected_rows)

        return True

    def verify_protection(self, output_path: Path, original_values: list[str]) -> bool:
        if not output_path.exists():
            return False
        with open(output_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        for val in original_values:
            if val and val in content:
                return False
        return True
