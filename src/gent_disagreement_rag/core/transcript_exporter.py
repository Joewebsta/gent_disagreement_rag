import json
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv


class TranscriptExporter:
    """Handles exporting formatted transcript segments to various output formats."""

    def __init__(self, output_dir: Path = None):
        load_dotenv()
        self.output_dir = output_dir or self._get_default_output_dir()
        self._ensure_output_directory()

    def _get_default_output_dir(self) -> Path:
        """Get default output directory from environment variable."""
        output_dir = os.getenv("TRANSCRIPT_FORMATTER_OUTPUT_DIR")
        if not output_dir:
            raise ValueError(
                "TRANSCRIPT_FORMATTER_OUTPUT_DIR environment variable not set"
            )
        return Path(output_dir).resolve()

    def _ensure_output_directory(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_segments(self, segments: List[Dict[str, str]], filename: str) -> Path:
        """Export formatted segments to JSON file."""
        output_file = self.output_dir / f"{filename}.json"

        with open(output_file, "w") as f:
            json.dump(segments, f, indent=2)

        return output_file
