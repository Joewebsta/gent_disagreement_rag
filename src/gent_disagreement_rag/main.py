"""
Main application for gent_disagreement_rag.

Before running this application, ensure the database is set up by running:
    poetry run seed-db

To reset the database (WARNING: deletes all data):
    poetry run reset-db
"""

from gent_disagreement_rag.core import PipelineOrchestrator


def main():
    """Main execution function."""

    orchestrator = PipelineOrchestrator()
    orchestrator.process_episodes()
    # orchestrator.format_existing_raw_transcripts()


if __name__ == "__main__":
    main()
