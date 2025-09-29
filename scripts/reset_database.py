#!/usr/bin/env python3
"""
Database reset script for gent_disagreement_rag.

This script drops all tables and recreates the database schema.
Use with caution as this will delete all data!
"""

import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from gent_disagreement_rag.core.database_manager import DatabaseManager


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def reset_database(db_manager: DatabaseManager) -> None:
    """Reset the database by dropping and recreating all tables."""
    logger = logging.getLogger(__name__)

    conn = db_manager.get_connection()
    cur = conn.cursor()

    try:
        logger.warning("Dropping all tables...")

        # Drop tables in reverse dependency order
        cur.execute("DROP TABLE IF EXISTS transcript_segments CASCADE;")
        cur.execute("DROP TABLE IF EXISTS episodes CASCADE;")

        # Drop the vector extension (optional, as it might be used by other databases)
        # cur.execute("DROP EXTENSION IF EXISTS vector CASCADE;")

        conn.commit()
        logger.info("All tables dropped successfully!")

        # Recreate schema and reseed data
        logger.info("Recreating database schema and data...")
        from .seed_database import create_schema, seed_episodes

        create_schema(db_manager)
        seed_episodes(db_manager)

        logger.info("Database reset completed successfully!")

    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def main() -> None:
    """Main function to reset the database."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Confirm destructive action
    print("\n" + "=" * 60)
    print("WARNING: This will DELETE ALL DATA in the database!")
    print("=" * 60)

    response = input("\nAre you sure you want to continue? (yes/no): ").lower().strip()

    if response not in ["yes", "y"]:
        logger.info("Database reset cancelled by user.")
        sys.exit(0)

    try:
        logger.info("Starting database reset process...")

        # Initialize database manager
        db_manager = DatabaseManager()

        # Reset database
        reset_database(db_manager)

        logger.info("Database reset completed successfully!")

    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
