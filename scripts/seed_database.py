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


def create_database_if_not_exists(db_manager: DatabaseManager) -> None:
    """Create the database if it doesn't exist."""
    logger = logging.getLogger(__name__)
    logger.info("Checking if database exists...")
    
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Get connection params
    params = db_manager.connection_params.copy()
    db_name = params.pop("database")
    
    # Connect to default postgres database to check/create target database
    params["database"] = "postgres"
    
    conn = psycopg2.connect(**params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Check if database exists
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cur.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cur.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Database '{db_name}' created successfully!")
        else:
            logger.info(f"Database '{db_name}' already exists.")
    finally:
        cur.close()
        conn.close()


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
    """Seed the database with initial episode data via the canonical SQL file."""
    logger = logging.getLogger(__name__)
    logger.info("Seeding episodes data from 002_seed_episodes.sql...")

    migrations_dir = Path(__file__).parent / "migrations"
    seed_file = migrations_dir / "002_seed_episodes.sql"

    if not seed_file.exists():
        raise FileNotFoundError(f"Seed file not found: {seed_file}")

    conn = db_manager.get_connection()
    cur = conn.cursor()

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            seed_sql = f.read()

        cur.execute(seed_sql)

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
        
        # Create database if it doesn't exist
        create_database_if_not_exists(db_manager)

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
