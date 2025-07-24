import re

from .normalizer import TextNormalizer


class TextPreprocessor:
    """Handles text preprocessing for better embedding quality."""

    def __init__(self):
        self.filler_patterns = [
            r"\b(um|uh|like|you know|i mean|sort of|kind of)\b",
            r"\b(so|well|right|okay)\b(?=\s+\w)",  # Only at start of sentences
            r"\[.*?\]",  # Remove bracketed content like [laughs], [singing]
        ]

    def preprocess_speaker_text(self, text: str) -> str:
        """
        Preprocess speaker text for better embedding quality.
        Removes filler words, normalizes text, and improves semantic coherence.
        """
        # Remove common filler words and phrases
        for pattern in self.filler_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Fix punctuation artifacts left by removed filler words
        text = self._fix_punctuation_artifacts(text)

        # Remove excessive punctuation
        text = re.sub(r"[.!?]{2,}", ".", text)
        text = re.sub(r"[,]{2,}", ",", text)

        # Normalize spacing
        text = TextNormalizer.normalize_spacing(text)

        # Remove very short segments (likely artifacts)
        if len(text.strip()) < 3:
            return ""

        return text

    def _fix_punctuation_artifacts(self, text: str) -> str:
        """Fix punctuation artifacts left by removed filler words."""
        # Handle cases like "Yes. My, my in-laws" -> "Yes. My in-laws"
        text = re.sub(r",\s*,", ",", text)  # Remove double commas
        text = re.sub(r",\s*\.", ".", text)  # Remove comma before period
        text = re.sub(r"\.\s*,", ".", text)  # Remove comma after period
        text = re.sub(r",\s*$", "", text)  # Remove trailing comma
        text = re.sub(r"^\s*,", "", text)  # Remove leading comma
        return text
