import json
import os
from pathlib import Path
from typing import List, Dict, Any


def load_processed_segments(file_name=None) -> List[Dict[str, Any]]:
    """
    Load processed segments from JSON file.

    Args:
        file_name: Optional name of the JSON file. If None, uses default location.

    Returns:
        List of processed segment dictionaries.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
    """

    base_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name

    file_path = Path(
        f"src/gent_disagreement_processor/data/processed/deepgram/{base_name}.json"
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Processed segments file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
