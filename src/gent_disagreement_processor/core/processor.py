import json
from pathlib import Path
from typing import List, Dict


class TranscriptFormatter:
    """Formats raw transcript data into structured segments for further processing."""

    def format_segments(self, transcript_path: Path) -> List[Dict[str, str]]:
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
