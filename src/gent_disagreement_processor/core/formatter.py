import json

from .normalizer import TextNormalizer


class DataFormatter:
    """Handles the initial formatting of raw segments."""

    def __init__(self):
        self.normalizer = TextNormalizer()

    def format_segments(self, file_name: str):
        file_path = (
            f"src/gent_disagreement_processor/data/raw/deepgram/{file_name}.json"
        )

        segments = []
        current_speaker = None

        with open(
            file_path,
            "r",
        ) as f:
            raw_transcript_data = json.load(f)

            paragraphs = raw_transcript_data["results"]["channels"][0]["alternatives"][
                0
            ]["paragraphs"]["paragraphs"]

            current_text = []

            for paragraph in paragraphs:
                speaker = str(paragraph["speaker"])

                # Map speaker IDs to names
                if speaker == "0":
                    speaker = "Ricky Ghoshroy"
                elif speaker == "1":
                    speaker = "Brendan Kelly"

                # If speaker changes, save current segment and start new one
                if current_speaker != speaker:
                    if current_text:
                        segments.append(
                            {
                                "speaker": current_speaker,
                                "text": " ".join(current_text).strip(),
                            }
                        )
                    current_speaker = speaker
                    current_text = []

                # Add sentences from this paragraph to current text
                current_text.extend(
                    sentence["text"] for sentence in paragraph["sentences"]
                )

            # Don't forget the last segment
            if current_text:
                segments.append(
                    {"speaker": current_speaker, "text": " ".join(current_text).strip()}
                )

        return segments

    # def format_segments2(self, segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    #     """Format raw segments into speaker chunks, excluding Scully."""
    #     formatted_segments = []

    #     # Initialize with the first segment (excluding Scully)
    #     current_speaker_chunk = None
    #     for segment in segments:
    #         if segment["speaker"]["name"] != "Scully":
    #             current_speaker_chunk = {
    #                 "speaker": segment["speaker"]["name"],
    #                 "text": self.normalizer.normalize_spacing(segment["text"]),
    #             }
    #             break

    #     for segment in segments[1:]:
    #         if segment["speaker"]["name"] == "Scully":
    #             continue

    #         if segment["speaker"]["name"] == current_speaker_chunk["speaker"]:
    #             # Same speaker - append text with normalized spacing
    #             combined_text = current_speaker_chunk["text"] + " " + segment["text"]
    #             current_speaker_chunk["text"] = self.normalizer.normalize_spacing(
    #                 combined_text
    #             )
    #         else:
    #             # Different speaker - save current chunk and start new one
    #             formatted_segments.append(current_speaker_chunk)
    #             current_speaker_chunk = {
    #                 "speaker": segment["speaker"]["name"],
    #                 "text": self.normalizer.normalize_spacing(segment["text"]),
    #             }

    #     # Don't forget to add the last chunk
    #     if current_speaker_chunk:
    #         formatted_segments.append(current_speaker_chunk)

    #     return formatted_segments
