from typing import List

from ..models import SpeakerSegment, SpeakerSummary


class StatisticsReporter:
    """Handles reporting statistics about processed data."""

    @staticmethod
    def print_statistics(
        processed_segments: List[SpeakerSegment],
        speaker_summaries: List[SpeakerSummary],
    ) -> None:
        """Print statistics about the processed data."""
        print("Processed segments written to processed_segments.json")
        print("Embedding-ready segments written to embedding_ready_segments.json")
        print(f"Total segments: {len(processed_segments)}")
        print(f"Processed segments for embedding: {len(processed_segments)}")
        print(f"Speaker summaries: {len(speaker_summaries)}")

        # Print statistics
        length_stats = {}
        for segment in processed_segments:
            category = segment.length_category
            if category not in length_stats:
                length_stats[category] = 0
            length_stats[category] += 1

        print("\nLength distribution:")
        for category, count in length_stats.items():
            print(f"  {category}: {count} segments")
