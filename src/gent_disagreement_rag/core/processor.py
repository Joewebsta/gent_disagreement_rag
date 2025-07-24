from typing import Any, Dict

from .formatter import DataFormatter
from .segment_processor import SegmentProcessor
from .speaker_summarizer import SpeakerSummarizer
from ..utils import DataExporter, StatisticsReporter


class AudioTranscriptProcessor:
    """Main orchestrator class that coordinates the entire processing pipeline."""

    def __init__(self):
        self.formatter = DataFormatter()
        self.processor = SegmentProcessor()
        self.summarizer = SpeakerSummarizer()
        self.exporter = DataExporter()
        self.reporter = StatisticsReporter()

    def process_transcript(self, data: Dict[str, Any]) -> None:
        """Process the complete transcript data."""
        segments = data["segments"]

        # Format segments
        formatted_segments = self.formatter.format_segments(segments)

        # Process segments for embedding preparation
        processed_segments = self.processor.process_speaker_segments(formatted_segments)

        # Create speaker summaries
        speaker_summaries = self.summarizer.create_speaker_summaries(processed_segments)

        # Export data
        self.exporter.export_data(processed_segments, speaker_summaries)

        # Report statistics
        self.reporter.print_statistics(processed_segments, speaker_summaries)
