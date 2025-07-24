from typing import List

from ..models import SpeakerSegment, SpeakerSummary
from .preprocessor import TextPreprocessor


class SpeakerSummarizer:
    """Creates summary representations for each speaker."""

    def __init__(self):
        self.preprocessor = TextPreprocessor()

    def create_speaker_summaries(
        self, speaker_segments: List[SpeakerSegment]
    ) -> List[SpeakerSummary]:
        """
        Create summary representations for each speaker.
        """
        speaker_data = {}

        for segment in speaker_segments:
            speaker = segment.speaker

            if speaker not in speaker_data:
                speaker_data[speaker] = {
                    "speaker": speaker,
                    "total_segments": 0,
                    "total_words": 0,
                    "text_chunks": [],
                    "length_categories": set(),
                }

            speaker_data[speaker]["total_segments"] += 1
            speaker_data[speaker]["total_words"] += segment.word_count
            speaker_data[speaker]["text_chunks"].append(segment.text)
            speaker_data[speaker]["length_categories"].add(segment.length_category)

        # Create summary objects
        summaries = []
        for speaker, data in speaker_data.items():
            # Combine all text for this speaker
            all_text = " ".join(data["text_chunks"])

            # Create a summary (first 200 words + last 200 words for long speakers)
            if len(all_text.split()) > 400:
                words = all_text.split()
                summary_text = " ".join(words[:200]) + " ... " + " ".join(words[-200:])
            else:
                summary_text = all_text

            summaries.append(
                SpeakerSummary(
                    speaker=speaker,
                    summary_text=self.preprocessor.preprocess_speaker_text(
                        summary_text
                    ),
                    total_segments=data["total_segments"],
                    total_words=data["total_words"],
                    length_categories=list(data["length_categories"]),
                )
            )

        return summaries
