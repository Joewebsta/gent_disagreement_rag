from dataclasses import dataclass
from typing import List


@dataclass
class SpeakerSummary:
    """Represents a summary of all segments for a speaker."""

    speaker: str
    summary_text: str
    total_segments: int
    total_words: int
    length_categories: List[str]
    type: str = "summary"
