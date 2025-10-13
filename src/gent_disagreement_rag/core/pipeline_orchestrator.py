import logging
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
        self.logger = logging.getLogger(__name__)
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
        """Process all unprocessed episodes through the full pipeline."""
        unprocessed = [ep for ep in self.episodes if not ep.get("processed", False)]
        total = len(unprocessed)
        self.logger.info(f"Starting pipeline processing for {total} episode(s)")

        for idx, episode in enumerate(self.episodes, 1):
            if self._should_skip_episode(episode):
                continue
            episode_info = self._get_episode_info(episode)
            self.logger.info(f"Processing {idx}/{total}: {episode_info}")
            self._process_single_episode(episode)

        self.logger.info(f"Pipeline processing complete. Processed {total} episode(s)")

    def format_existing_raw_transcripts(self):
        """Format existing raw transcripts without transcription."""
        unprocessed = [ep for ep in self.episodes if not ep.get("processed", False)]
        total = len(unprocessed)
        self.logger.info(f"Starting formatting for {total} episode(s)")

        for idx, episode in enumerate(self.episodes, 1):
            if self._should_skip_episode(episode):
                continue
            episode_info = self._get_episode_info(episode)
            self.logger.info(f"Formatting {idx}/{total}: {episode_info}")
            self._format_single_episode(episode)

        self.logger.info(f"Formatting complete. Formatted {total} episode(s)")

    def _get_episode_info(self, episode: dict) -> str:
        """Get a concise episode identifier for logging."""
        episode_id = episode.get("episode_id", "unknown")
        file_name = episode.get("file_name", "unknown")
        return f"{episode_id} ({file_name})"

    def _should_skip_episode(self, episode: dict) -> bool:
        """
        Check if episode has already been processed.

        Args:
            episode: Episode dictionary with metadata

        Returns:
            True if episode should be skipped, False otherwise
        """
        if episode.get("processed", False):
            episode_info = self._get_episode_info(episode)
            self.logger.info(f"⏭️  Skipping {episode_info} - already processed")
            return True
        return False

    def _process_single_episode(self, episode: dict) -> None:
        """
        Process a single episode through the full pipeline.

        Pipeline stages:
        1. Transcribe audio file
        2. Format transcript segments
        3. Export formatted segments
        4. Generate embeddings
        5. Store embeddings in database

        Args:
            episode: Episode dictionary with metadata

        Raises:
            Exception: If any pipeline stage fails
        """
        speakers_map = episode["speakers_map"]
        file_name = episode["file_name"]
        episode_id = episode["episode_id"]

        # Transcribe audio file
        self.logger.info(f"  → Transcribing audio")
        raw_transcript_path = self.audio_transcriber.generate_transcript(file_name)
        
        if raw_transcript_path is None:
            self.logger.error(f"  ✗ Transcription failed - skipping episode")
            return
        
        self.logger.info(f"  ✓ Transcription complete")

        # Format and export the raw transcript
        self.logger.info(f"  → Formatting transcript")
        processed_transcript_path = self._format_and_export_raw_transcript(
            raw_transcript_path, speakers_map
        )
        self.logger.info(f"  ✓ Formatting complete")

        # Generate embeddings
        self.logger.info(f"  → Generating embeddings")
        segments = load_processed_segments(Path(processed_transcript_path))
        embeddings = self.embedding_service.generate_embeddings(segments)
        self.logger.info(f"  ✓ Generated {len(embeddings)} embeddings")

        # Store the embeddings in the database
        self.logger.info(f"  → Storing embeddings")
        self.database_manager.store_embeddings(embeddings, episode_id)
        self.logger.info(f"  ✓ Stored {len(embeddings)} embeddings")
        self.logger.info(f"✓ Completed processing")

    def _format_single_episode(self, episode: dict) -> None:
        """
        Format an existing raw transcript for a single episode.

        Pipeline stages:
        1. Format transcript segments
        2. Export formatted segments

        Args:
            episode: Episode dictionary with metadata including raw_transcript_path

        Raises:
            Exception: If formatting/export fails
        """
        speakers_map = episode["speakers_map"]
        raw_transcript_path = Path(episode["raw_transcript_path"])

        # Format and export the raw transcript
        self.logger.info(f"  → Formatting raw transcript")
        self._format_and_export_raw_transcript(raw_transcript_path, speakers_map)
        self.logger.info(f"  ✓ Formatting complete")
        self.logger.info(f"✓ Completed formatting")

    def _format_and_export_raw_transcript(
        self, raw_transcript_path: Path, speakers_map: dict
    ) -> Path:
        formatted_segments = self.transcript_formatter.format_segments(
            raw_transcript_path, speakers_map
        )

        return self.transcript_exporter.export_segments(
            formatted_segments, raw_transcript_path.stem
        )
