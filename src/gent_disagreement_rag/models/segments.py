from dataclasses import dataclass
from typing import Optional


@dataclass
class Episode:
    """Represents an episode with metadata."""

    episode_number: str
    title: Optional[str] = None
    file_name: Optional[str] = None


@dataclass
class SpeakerSegment:
    """Represents a processed speaker segment with metadata."""

    speaker: str
    text: str
    episode_id: Optional[int] = None
