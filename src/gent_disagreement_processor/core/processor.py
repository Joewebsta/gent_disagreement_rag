import json
import os
from pathlib import Path
from typing import List, Dict, Any

from .normalizer import TextNormalizer


class TranscriptFormatter:
    """Formats raw transcript data into structured segments for further processing."""

    def __init__(self):
        self.normalizer = TextNormalizer()

    def process_transcript(self, transcript_path: Path) -> None:
        """Process the raw transcript data and export formatted segments to JSON file."""
        formatted_segments = self._format_segments(transcript_path)
        self._export_segments(formatted_segments, transcript_path)

    def _format_segments(self, transcript_path: Path) -> List[Dict[str, str]]:
        """Format raw transcript data into structured segments."""

        segments = []
        current_speaker = None

        with open(transcript_path, "r") as f:
            raw_transcript_data = json.load(f)

            paragraphs = raw_transcript_data["results"]["channels"][0]["alternatives"][
                0
            ]["paragraphs"]["paragraphs"]

            current_text = []

            for paragraph in paragraphs:
                speaker = str(paragraph["speaker"])

                # Map speaker IDs to names
                if speaker == "0":
                    speaker = "Ricky Ghoshroy"
                elif speaker == "1":
                    speaker = "Brendan Kelly"

                # If speaker changes, save current segment and start new one
                if current_speaker != speaker:
                    if current_text:
                        segments.append(
                            {
                                "speaker": current_speaker,
                                "text": " ".join(current_text).strip(),
                            }
                        )
                    current_speaker = speaker
                    current_text = []

                # Add sentences from this paragraph to current text
                current_text.extend(
                    sentence["text"] for sentence in paragraph["sentences"]
                )

            # Don't forget the last segment
            if current_text:
                segments.append(
                    {"speaker": current_speaker, "text": " ".join(current_text).strip()}
                )

        return segments

    def _export_segments(self, segments: List[Dict[str, str]], file_name: Path) -> None:
        """Export formatted segments to JSON file."""
        output_dir = "src/gent_disagreement_processor/data/processed/transcripts/"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract just the filename from the full path
        filename = os.path.basename(file_name)
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename

        # Save segments to JSON file
        output_file = os.path.join(output_dir, f"{base_name}.json")
        with open(output_file, "w") as f:
            json.dump(segments, f, indent=2)

        print(f"Exported {len(segments)} segments to {output_file}")
