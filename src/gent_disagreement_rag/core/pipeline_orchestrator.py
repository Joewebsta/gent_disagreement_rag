from pathlib import Path
from gent_disagreement_rag.config import load_episodes
from gent_disagreement_rag.core import (
    AudioTranscriber,
    DatabaseManager,
    EmbeddingService,
    TranscriptExporter,
    TranscriptFormatter,
)
from gent_disagreement_rag.utils import load_processed_segments


class PipelineOrchestrator:
    def __init__(self):
        self.database_manager = DatabaseManager()

        # Verify database connection
        try:
            self.database_manager.validate_connection()
        except ConnectionError as e:
            print(f"❌ {e}")
            raise

        self.audio_transcriber = AudioTranscriber()
        self.embedding_service = EmbeddingService()
        self.transcript_exporter = TranscriptExporter()
        self.transcript_formatter = TranscriptFormatter()
        self.episodes = load_episodes()

    def process_episodes(self):
        for episode in self.episodes:
            # Skip already processed episodes
            if episode.get("processed", False):
                print(
                    f"⏭️  Skipping episode {episode['episode_id']} - already processed"
                )
                continue

            speakers_map = episode["speakers_map"]
            file_name = episode["file_name"]
            episode_id = episode["episode_id"]

            # Transcribe audio file
            raw_transcript_path = self.audio_transcriber.generate_transcript(file_name)

            # Format the transcript data
            formatted_segments = self.transcript_formatter.format_segments(
                raw_transcript_path, speakers_map
            )

            # Export the formatted data
            processed_transcript_path = self.transcript_exporter.export_segments(
                formatted_segments, raw_transcript_path.stem
            )

            # Generate embeddings
            segments = load_processed_segments(Path(processed_transcript_path))
            embeddings = self.embedding_service.generate_embeddings(segments)

            # Store the embeddings in the database
            self.database_manager.store_embeddings(embeddings, episode_id)

    def format_existing_raw_transcripts(self):
        for episode in self.episodes:
            if episode.get("processed", False):
                print(
                    f"⏭️  Skipping episode {episode['episode_id']} - already processed"
                )
                continue

            speakers_map = episode["speakers_map"]
            raw_transcript_path = Path(episode["raw_transcript_path"])

            # Format the transcript data
            formatted_segments = self.transcript_formatter.format_segments(
                raw_transcript_path, speakers_map
            )

            # Export the formatted data
            self.transcript_exporter.export_segments(
                formatted_segments, raw_transcript_path.stem
            )
