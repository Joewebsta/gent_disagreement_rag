from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeakerSegment:
    """Represents a processed speaker segment with metadata."""

    speaker: str
    text: str
    type: str
    word_count: int
    length_category: str
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    original_length: Optional[int] = None
