import json
import os
from typing import List, Any


class DataExporter:
    """Handles exporting processed data to JSON files."""

    @staticmethod
    def export_data(
        segments: List[Any],
        file_name: str = None,
        output_dir: str = "src/gent_disagreement_processor/data/processed/transcripts/",
    ) -> None:
        """Export processed data to JSON files."""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Handle both objects and dictionaries
        def segment_to_dict(segment):
            if hasattr(segment, "__dict__"):
                return vars(segment)
            elif isinstance(segment, dict):
                return segment
            else:
                return str(segment)

        # Save segments to JSON file
        output_file = os.path.join(output_dir, f"{file_name}.json")
        with open(output_file, "w") as f:
            json.dump([segment_to_dict(segment) for segment in segments], f, indent=2)

        print(f"Exported {len(segments)} segments to {output_file}")

    # @staticmethod
    # def export_data(
    #     processed_segments: List[SpeakerSegment],
    #     speaker_summaries: List[SpeakerSummary],
    #     output_dir: str = "src/gent_disagreement_processor/data/processed/",
    # ) -> None:
    #     """Export processed data to JSON files."""
    #     # Ensure output directory exists
    #     os.makedirs(output_dir, exist_ok=True)

    #     # Combine all processed data
    #     embedding_ready_data = {
    #         "processed_segments": [vars(segment) for segment in processed_segments],
    #         "speaker_summaries": [vars(summary) for summary in speaker_summaries],
    #         "metadata": {
    #             "total_segments": len(processed_segments),
    #             "total_speakers": len(speaker_summaries),
    #             "processing_strategy": "variable_length_optimization",
    #         },
    #     }

    #     # Write formatted segments to JSON file (original format for compatibility)
    #     with open(f"{output_dir}processed_segments.json", "w") as f:
    #         json.dump([vars(segment) for segment in processed_segments], f, indent=2)

    #     # Write embedding-ready data to separate file
    #     with open(f"{output_dir}embedding_ready_segments.json", "w") as f:
    #         json.dump(embedding_ready_data, f, indent=2)
