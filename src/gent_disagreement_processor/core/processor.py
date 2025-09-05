from ..utils import DataExporter
from .formatter import DataFormatter


class TranscriptFormatter:
    """Formats raw transcript data into structured segments for further processing."""

    def __init__(self):
        self.formatter = DataFormatter()
        self.exporter = DataExporter()

    def process_transcript(self, file_name: str) -> None:
        """Process the raw transcript data. Export the formatted segments to a JSON file."""

        # Format segments
        formatted_segments = self.formatter.format_segments(file_name)

        # Export segments to JSON file
        self.exporter.export_data(formatted_segments, file_name)
