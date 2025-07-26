from .core import AudioTranscriptProcessor, DatabaseManager, EmbeddingService
from .data import raw_transcript_data
from .utils import load_processed_segments


def main():
    """Main execution function."""
    # Process the transcript
    # processor = AudioTranscriptProcessor()
    # processor.process_transcript(raw_transcript_data)

    # Setup the database
    # database_manager = DatabaseManager()
    # database_manager.setup_database()

    # Generate embeddings
    segments = load_processed_segments()
    embedding_service = EmbeddingService()
    embedding_service.generate_and_store_embeddings(segments)
