import json
import os
from pathlib import Path
from typing import List, Dict, Any


def load_processed_segments(file_path=None) -> List[Dict[str, Any]]:
    """
    Load processed segments from JSON file.
    
    Args:
        file_path: Optional path to the JSON file. If None, uses default location.
        
    Returns:
        List of processed segment dictionaries.
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist.
    """
    if file_path is None:
        # Default to the standard processed segments location
        current_dir = Path(__file__).parent.parent
        file_path = current_dir / "data/processed/processed_segments.json"
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Processed segments file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)