#!/usr/bin/env python3
"""
Database seeding script for gent_disagreement_rag.

This script sets up the database schema and seeds it with initial data.
It can be run independently of the main application.
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


def create_schema(db_manager: DatabaseManager) -> None:
    """Create the database schema by running migration files."""
    logger = logging.getLogger(__name__)
    logger.info("Creating database schema...")

    # Get the migrations directory (in the same directory as this script)
    migrations_dir = Path(__file__).parent / "migrations"

    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    # Get all SQL migration files and sort them
    migration_files = sorted([f for f in migrations_dir.glob("*.sql")])

    if not migration_files:
        logger.warning("No migration files found")
        return

    conn = db_manager.get_connection()
    cur = conn.cursor()

    try:
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")

            with open(migration_file, "r") as f:
                migration_sql = f.read()

            cur.execute(migration_sql)

        conn.commit()
        logger.info("All migrations completed successfully!")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def seed_episodes(db_manager: DatabaseManager) -> None:
    """Seed the database with initial episode data."""
    logger = logging.getLogger(__name__)
    logger.info("Seeding episodes data...")

    conn = db_manager.get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO episodes (
                episode_number,
                title,
                file_name, 
                date_published
            ) VALUES 
                ('180', 'A SCOTUS ''24-''25" term review with Professor Jack Beermann', 'AGD-180.mp3', '2025-08-12'),
                ('181', 'Six in Sixty: creeping authoritarianism', 'AGD-181.mp3', '2025-08-26')
            ON CONFLICT (episode_number) DO NOTHING;
            """
        )
        conn.commit()
        logger.info("Episodes data seeded successfully!")
    except Exception as e:
        logger.error(f"Error seeding episodes: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def main() -> None:
    """Main function to seed the database."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting database seeding process...")

        # Initialize database manager
        db_manager = DatabaseManager()

        # Create schema (run migrations)
        create_schema(db_manager)

        # Seed episodes data
        seed_episodes(db_manager)

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
