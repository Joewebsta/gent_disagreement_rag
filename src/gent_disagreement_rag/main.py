"""
Main application for gent_disagreement_rag.

Before running this application, ensure the database is set up by running:
    poetry run seed-db

To reset the database (WARNING: deletes all data):
    poetry run reset-db
"""

import logging

from gent_disagreement_rag.core import PipelineOrchestrator


def main():
    """Main execution function."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    # Suppress noisy HTTP logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    orchestrator = PipelineOrchestrator()
    orchestrator.process_episodes()
    # orchestrator.format_existing_raw_transcripts()


if __name__ == "__main__":
    main()
