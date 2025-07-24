from .core import AudioTranscriptProcessor
from .data import raw_transcript_data


def main():
    """Main execution function."""
    processor = AudioTranscriptProcessor()
    processor.process_transcript(raw_transcript_data)
