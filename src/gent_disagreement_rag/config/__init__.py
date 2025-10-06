"""Configuration module for episode management."""

import json
from pathlib import Path
from typing import List, TypedDict


class Episode(TypedDict):
    """Type definition for episode configuration."""

    episode_id: int
    file_name: str
    processed_transcript_path: str
    processed: bool


def load_episodes() -> List[Episode]:
    """
    Load episode configuration from episodes.json.

    Returns:
        List of episode dictionaries with metadata and processing status.
    """
    config_path = Path(__file__).parent / "episodes.json"
    with open(config_path, "r") as f:
        return json.load(f)


__all__ = ["load_episodes", "Episode"]
