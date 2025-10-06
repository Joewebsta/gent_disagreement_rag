"""
Main application for gent_disagreement_rag.

Before running this application, ensure the database is set up by running:
    poetry run seed-db

To reset the database (WARNING: deletes all data):
    poetry run reset-db
"""

from gent_disagreement_processor.core import (
    AudioTranscriber,
    DatabaseManager,
    EmbeddingService,
    TranscriptExporter,
    TranscriptFormatter,
)
from gent_disagreement_processor.utils import load_processed_segments


def main():
    """Main execution function."""

    # Initialize database manager (assumes database is already set up via scripts)
    database_manager = DatabaseManager()

    # Verify database connection
    try:
        database_manager.get_connection().close()
    except Exception as e:
        print("❌ Database connection failed!")
        print("Please run 'poetry run seed-db' to set up the database first.")
        print(f"Error: {e}")
        return

    # Initialize services
    audio_transcriber = AudioTranscriber()
    formatter = TranscriptFormatter()
    exporter = TranscriptExporter()
    embedding_service = EmbeddingService()

    episodes = [
        {"episode_id": 1, "file_name": "AGD-180.mp3"},
        {"episode_id": 2, "file_name": "AGD-181.mp3"},
        {"episode_id": 3, "file_name": "AGD-182.mp3"},
    ]

    for episode in episodes:
        file_name = episode["file_name"]
        episode_id = episode["episode_id"]

        # Transcribe audio file
        raw_transcript_path = audio_transcriber.generate_transcript(file_name)

        # Format the transcript data
        formatted_segments = formatter.format_segments(raw_transcript_path)

        # Export the formatted data
        processed_transcript_path = exporter.export_segments(
            formatted_segments, raw_transcript_path.stem
        )

        # Generate embeddings
        segments = load_processed_segments(processed_transcript_path)
        embeddings = embedding_service.generate_embeddings(segments)

        # Store the embeddings in the database
        database_manager.store_embeddings(embeddings, episode_id)


if __name__ == "__main__":
    main()
