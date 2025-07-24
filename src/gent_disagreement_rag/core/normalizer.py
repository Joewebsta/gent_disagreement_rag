import re


class TextNormalizer:
    """Handles text normalization and spacing consistency."""

    @staticmethod
    def normalize_spacing(text: str) -> str:
        """Normalize spacing to ensure consistent single spaces after periods and between words."""
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)

        # Protect ellipses by temporarily replacing them
        text = re.sub(r"\.{3,}", "ELLIPSIS_PLACEHOLDER", text)

        # Ensure single space after periods, exclamation marks, and question marks
        text = re.sub(r"([.!?])\s*", r"\1 ", text)

        # Restore ellipses
        text = text.replace("ELLIPSIS_PLACEHOLDER", "...")

        # Remove leading/trailing whitespace
        text = text.strip()
        return text
