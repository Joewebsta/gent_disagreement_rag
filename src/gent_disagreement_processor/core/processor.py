import json
import os
from typing import List, Dict, Any

from .normalizer import TextNormalizer


class TranscriptFormatter:
    """Formats raw transcript data into structured segments for further processing."""

    def __init__(self):
        self.normalizer = TextNormalizer()

    def process_transcript(self, transcript_path: str) -> None:
        """Process the raw transcript data and export formatted segments to JSON file."""
        formatted_segments = self._format_segments(transcript_path)
        self._export_segments(formatted_segments, transcript_path)

    def _format_segments(self, transcript_path: str) -> List[Dict[str, str]]:
        """Format raw transcript data into structured segments."""
        # Remove any file extension and add .json
        base_name = (
            transcript_path.rsplit(".", 1)[0]
            if "." in transcript_path
            else transcript_path
        )
        transcript_path = (
            f"src/gent_disagreement_processor/data/raw/transcripts/{base_name}.json"
        )

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

    def _export_segments(self, segments: List[Dict[str, str]], file_name: str) -> None:
        """Export formatted segments to JSON file."""
        output_dir = "src/gent_disagreement_processor/data/processed/transcripts/"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Remove any file extension from the file name
        base_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name

        # Save segments to JSON file
        output_file = os.path.join(output_dir, f"{base_name}.json")
        with open(output_file, "w") as f:
            json.dump(segments, f, indent=2)

        print(f"Exported {len(segments)} segments to {output_file}")
