from typing import Dict, List

from ..models import SpeakerSegment
from ..utils import LengthCategorizer, TextChunker
from .preprocessor import TextPreprocessor


class SegmentProcessor:
    """Main processor for speaker segments."""

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.chunker = TextChunker()
        self.categorizer = LengthCategorizer()

    def process_speaker_segments(
        self, speaker_segments: List[Dict[str, str]]
    ) -> List[SpeakerSegment]:
        """
        Process speaker segments with variable text lengths for optimal embedding preparation.
        """
        processed_segments = []

        for segment in speaker_segments:
            speaker = segment["speaker"]
            text = segment["text"]

            # Preprocess the text
            cleaned_text = self.preprocessor.preprocess_speaker_text(text)

            if not cleaned_text:
                continue

            # Determine strategy based on length
            word_count = len(cleaned_text.split())
            length_category = self.categorizer.categorize_text_length(word_count)

            if length_category == "short":
                processed_segments.append(
                    SpeakerSegment(
                        speaker=speaker,
                        text=cleaned_text,
                        type="short",
                        word_count=word_count,
                        length_category=length_category,
                    )
                )

            elif length_category == "medium":
                processed_segments.append(
                    SpeakerSegment(
                        speaker=speaker,
                        text=cleaned_text,
                        type="medium",
                        word_count=word_count,
                        length_category=length_category,
                    )
                )

            else:
                # Long speaker - chunk into overlapping segments
                chunks = self.chunker.chunk_text(cleaned_text)

                for i, chunk in enumerate(chunks):
                    chunk_word_count = len(chunk.split())
                    processed_segments.append(
                        SpeakerSegment(
                            speaker=speaker,
                            text=chunk,
                            type="chunk",
                            chunk_index=i,
                            total_chunks=len(chunks),
                            word_count=chunk_word_count,
                            length_category=length_category,
                            original_length=word_count,
                        )
                    )

        return processed_segments
