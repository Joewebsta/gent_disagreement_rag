from gent_disagreement_processor.core import (
    TranscriptFormatter,
    TranscriptExporter,
    DatabaseManager,
    EmbeddingService,
    AudioTranscriber,
)
from gent_disagreement_processor.utils import load_processed_segments
from gent_disagreement_processor.core import ChatManager
from pathlib import Path


def main():
    """Main execution function."""

    # # # Setup the database
    # database_manager = DatabaseManager()
    # database_manager.setup_database()

    # episodes = [
    #     {"episode_number": 180, "file_name": "AGD-180.mp3", "episode_id": 1},
    #     {"episode_number": 181, "file_name": "AGD-181.mp3", "episode_id": 2},
    # ]

    file_name = "AGD-180-7.m4a"

    # # Transcribe audio file
    # # AudioTranscriber handles transcription of audio files using Deepgram's API
    # # It validates the audio file, creates a Deepgram client, transcribes the audio,
    # # and saves the transcript as a JSON file
    # audio_transcriber = AudioTranscriber()
    # raw_transcript_path = audio_transcriber.generate_transcript(file_name)

    # print("raw_transcript_path", raw_transcript_path)

    # Process the raw transcript with separated concerns
    raw_transcript_path = Path(
        "/Users/jwebster/Home/Code/projects/2025-projects/!Starred/gent_disagreement_processor/src/gent_disagreement_processor/data/raw/transcripts/AGD-180-7.json"
    )

    # Separate formatting and exporting
    formatter = TranscriptFormatter()
    exporter = TranscriptExporter()

    # Format the transcript data
    formatted_segments = formatter.format_segments(raw_transcript_path)

    # Export the formatted data
    output_path = exporter.export_segments(formatted_segments, raw_transcript_path.stem)

    # Generate embeddings
    # for episode in episodes:
    #     file_name = f"AGD-{episode['episode_number']}.mp3"
    #     episode_id = episode["episode_id"]

    #     segments = load_processed_segments(file_name)
    #     embedding_service = EmbeddingService()
    #     embedding_service.generate_and_store_embeddings(segments, episode_id)

    # # Run the chatbot
    # chat_manager = ChatManager()
    # chat_manager.run()


# poetry run python src/gent_disagreement_processor/main.py

if __name__ == "__main__":
    main()
