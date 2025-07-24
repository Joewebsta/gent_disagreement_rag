class LengthCategorizer:
    """Categorizes text length for appropriate processing strategy."""

    @staticmethod
    def categorize_text_length(word_count: int) -> str:
        """
        Categorize text length for appropriate processing strategy.
        Returns: 'short', 'medium', or 'long'
        """
        if word_count < 100:
            return "short"
        elif word_count < 500:
            return "medium"
        else:
            return "long"
