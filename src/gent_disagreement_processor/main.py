from gent_disagreement_processor.core import (
    AudioTranscriber,
    ChatManager,
    DatabaseManager,
    EmbeddingService,
    TranscriptExporter,
    TranscriptFormatter,
)
from gent_disagreement_processor.utils import load_processed_segments


def main():
    """Main execution function."""

    # Setup the database
    database_manager = DatabaseManager()
    database_manager.setup_database()

    episodes = [
        {"episode_id": 1, "file_name": "AGD-180.mp3"},
        {"episode_id": 2, "file_name": "AGD-181.mp3"},
        {"episode_id": 3, "file_name": "AGD-182-7.m4a"},
    ]

    for episode in episodes:
        episode_id = episode["episode_id"]
        file_name = episode["file_name"]

        # Transcribe audio file
        audio_transcriber = AudioTranscriber()
        raw_transcript_path = audio_transcriber.generate_transcript(file_name)

        # Format the transcript data
        formatter = TranscriptFormatter()
        formatted_segments = formatter.format_segments(raw_transcript_path)

        # Export the formatted data
        exporter = TranscriptExporter()
        processed_transcript_path = exporter.export_segments(
            formatted_segments, raw_transcript_path.stem
        )

        # Generate embeddings
        segments = load_processed_segments(processed_transcript_path)
        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(segments)

        # Store the embeddings in the database
        database_manager.store_embeddings(embeddings, episode_id)

    # # # Run the chatbot
    # chat_manager = ChatManager()
    # chat_manager.run()


# poetry run python src/gent_disagreement_processor/main.py

if __name__ == "__main__":
    main()
