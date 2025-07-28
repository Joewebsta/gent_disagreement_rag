from typing import Any, Dict, List

from .normalizer import TextNormalizer


class DataFormatter:
    """Handles the initial formatting of raw segments."""

    def __init__(self):
        self.normalizer = TextNormalizer()

    def format_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format raw segments into speaker chunks, excluding Scully."""
        formatted_segments = []

        # Initialize with the first segment (excluding Scully)
        current_speaker_chunk = None
        for segment in segments:
            if segment["speaker"]["name"] != "Scully":
                current_speaker_chunk = {
                    "speaker": segment["speaker"]["name"],
                    "text": self.normalizer.normalize_spacing(segment["text"]),
                }
                break

        for segment in segments[1:]:
            if segment["speaker"]["name"] == "Scully":
                continue

            if segment["speaker"]["name"] == current_speaker_chunk["speaker"]:
                # Same speaker - append text with normalized spacing
                combined_text = current_speaker_chunk["text"] + " " + segment["text"]
                current_speaker_chunk["text"] = self.normalizer.normalize_spacing(
                    combined_text
                )
            else:
                # Different speaker - save current chunk and start new one
                formatted_segments.append(current_speaker_chunk)
                current_speaker_chunk = {
                    "speaker": segment["speaker"]["name"],
                    "text": self.normalizer.normalize_spacing(segment["text"]),
                }

        # Don't forget to add the last chunk
        if current_speaker_chunk:
            formatted_segments.append(current_speaker_chunk)

        return formatted_segments
