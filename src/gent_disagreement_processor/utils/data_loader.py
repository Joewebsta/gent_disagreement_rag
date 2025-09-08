import json
import os
from pathlib import Path
from typing import List, Dict, Any


def load_processed_segments(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load processed segments from JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        List of processed segment dictionaries.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Processed segments file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
