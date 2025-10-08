# TranscriptFormatter Improvements

This document outlines suggested improvements to the `TranscriptFormatter` class to enhance maintainability, error handling, and code quality.

## Current Implementation

The `TranscriptFormatter.format_segments()` method currently accepts a transcript path and speaker mapping dictionary, then processes Deepgram transcript JSON into structured segments.

## Suggested Improvements

### 1. Add Type Hints for Clarity

**Current:**
```python
from typing import List, Dict
```

**Improved:**
```python
from typing import List, Dict, Any
```

Add `Any` for better type hinting of JSON structures.

---

### 2. Extract Magic Path Navigation ⭐ High Priority

**Current (Lines 20-22):**
```python
paragraphs = raw_transcript_data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
```

**Improved:**
```python
def _get_paragraphs(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract paragraphs from Deepgram response structure."""
    return raw_data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
```

**Benefits:**
- Isolates fragile nested dictionary access
- Makes the main logic more readable
- Easier to update if Deepgram API changes
- Enables better error handling

---

### 3. Add Error Handling for Malformed Transcripts ⭐ High Priority

**Current:**
No error handling - will raise cryptic `KeyError` or `IndexError` if transcript format is invalid.

**Improved:**
```python
try:
    paragraphs = self._get_paragraphs(raw_transcript_data)
except (KeyError, IndexError) as e:
    raise ValueError(f"Invalid transcript format in {transcript_path}: {e}")
```

**Benefits:**
- Provides clear error messages
- Prevents application crashes from malformed data
- Makes debugging easier

---

### 4. Extract Segment Building Logic (DRY Principle) ⭐ High Priority

**Current:**
Segment creation logic is duplicated on:
- Lines 33-37 (when speaker changes)
- Lines 50-52 (final segment)

**Improved:**
```python
def _create_segment(self, speaker: str, text_parts: List[str]) -> Dict[str, str]:
    """Create a segment dictionary from speaker and text parts."""
    return {
        "speaker": speaker,
        "text": " ".join(text_parts).strip()
    }
```

Then use:
```python
segments.append(self._create_segment(current_speaker, current_text))
```

**Benefits:**
- Eliminates code duplication
- Single source of truth for segment structure
- Easier to modify segment format in future

---

### 5. Make speakers_map Optional

**Current:**
```python
def format_segments(
    self, transcript_path: Path, speakers_map: Dict[str, str]
) -> List[Dict[str, str]]:
```

**Improved:**
```python
def format_segments(
    self,
    transcript_path: Path,
    speakers_map: Dict[str, str] | None = None
) -> List[Dict[str, str]]:
    """Format raw transcript data into structured segments.

    Args:
        transcript_path: Path to the raw Deepgram transcript JSON
        speakers_map: Optional mapping of speaker IDs to names.
                     If not provided, speakers will be labeled as "Speaker {id}"
    """
    speakers_map = speakers_map or {}
    # ... rest of code
```

**Benefits:**
- More flexible API
- Can process transcripts without pre-configured speaker names
- Maintains backward compatibility

---

### 6. Add Validation for Empty Segments

**Current:**
Could potentially create segments with empty text if `current_text` list is empty or contains only whitespace.

**Improved:**
```python
if current_text:
    text = " ".join(current_text).strip()
    if text:  # Only create segment if there's actual content
        segments.append(self._create_segment(current_speaker, current_text))
```

**Benefits:**
- Prevents empty segments in output
- Cleaner data for downstream processing
- Handles edge cases gracefully

---

## Implementation Priority

### High Priority (Most Impactful)
1. **#2 - Extract magic path navigation** - Prevents crashes and improves maintainability
2. **#3 - Add error handling** - Essential for production robustness
3. **#4 - Extract segment creation** - Eliminates duplication (DRY principle)

### Medium Priority
4. **#5 - Optional speakers_map** - Improves API flexibility
5. **#6 - Empty segment validation** - Data quality improvement

### Low Priority
6. **#1 - Type hints** - Nice to have, minimal functional impact

---

## Full Refactored Example

```python
import json
from pathlib import Path
from typing import List, Dict, Any


class TranscriptFormatter:
    """Formats raw transcript data into structured segments for further processing."""

    def format_segments(
        self,
        transcript_path: Path,
        speakers_map: Dict[str, str] | None = None
    ) -> List[Dict[str, str]]:
        """Format raw transcript data into structured segments.

        Args:
            transcript_path: Path to the raw Deepgram transcript JSON
            speakers_map: Optional mapping of speaker IDs to names

        Returns:
            List of segment dictionaries with 'speaker' and 'text' keys

        Raises:
            ValueError: If transcript format is invalid
        """
        speakers_map = speakers_map or {}
        segments = []
        current_speaker = None
        current_text = []

        with open(transcript_path, "r") as f:
            raw_transcript_data = json.load(f)

            try:
                paragraphs = self._get_paragraphs(raw_transcript_data)
            except (KeyError, IndexError) as e:
                raise ValueError(f"Invalid transcript format in {transcript_path}: {e}")

            for paragraph in paragraphs:
                speaker_id = str(paragraph["speaker"])
                speaker = speakers_map.get(speaker_id, f"Speaker {speaker_id}")

                # If speaker changes, save current segment and start new one
                if current_speaker != speaker:
                    if current_text:
                        segments.append(self._create_segment(current_speaker, current_text))
                    current_speaker = speaker
                    current_text = []

                # Add sentences from this paragraph to current text
                current_text.extend(
                    sentence["text"] for sentence in paragraph["sentences"]
                )

            # Don't forget the last segment
            if current_text:
                segments.append(self._create_segment(current_speaker, current_text))

        return segments

    def _get_paragraphs(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract paragraphs from Deepgram response structure.

        Args:
            raw_data: Raw Deepgram transcript JSON

        Returns:
            List of paragraph dictionaries

        Raises:
            KeyError: If expected keys are missing
            IndexError: If expected array indices don't exist
        """
        return raw_data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]

    def _create_segment(self, speaker: str, text_parts: List[str]) -> Dict[str, str]:
        """Create a segment dictionary from speaker and text parts.

        Args:
            speaker: Speaker name or identifier
            text_parts: List of text strings to join

        Returns:
            Dictionary with 'speaker' and 'text' keys
        """
        text = " ".join(text_parts).strip()
        if not text:
            return None  # Or handle empty segments as needed

        return {
            "speaker": speaker,
            "text": text
        }
```

---

## Notes

- All improvements are backward compatible
- No changes to external API (except making speakers_map optional)
- Maintains current functionality while improving maintainability
- Can be implemented incrementally
