import logging
import os
from typing import List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


class DatabaseManager:
    """
    Manages database connections and operations for the A Gentleman's Disagreement RAG application.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        """
        Initialize the database manager with connection parameters.
        Loads from environment variables with sensible defaults.
        """
        # Load environment variables
        load_dotenv()

        self.connection_params = {
            "host": host or os.getenv("DB_HOST", "localhost"),
            "port": port or int(os.getenv("DB_PORT", "5432")),
            "user": user or os.getenv("DB_USER", "postgres"),
            "password": password
            or os.getenv("DB_PASSWORD", ""),  # No default for security
            "database": database or os.getenv("DB_NAME", "gent_disagreement"),
        }

        if not self.connection_params["password"]:
            raise ValueError(
                "Database password must be provided via DB_PASSWORD environment variable"
            )

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def validate_connection(self) -> bool:
        """
        Validate that a database connection can be established.

        Returns:
            bool: True if connection is successful

        Raises:
            ConnectionError: If connection fails with detailed error message
        """
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except Exception as e:
            raise ConnectionError(
                f"Database connection failed!\n"
                f"Please run 'poetry run seed-db' to set up the database first.\n"
                f"Error: {e}"
            )

    def get_connection(self):
        """
        Create and return a database connection.
        """
        return psycopg2.connect(**self.connection_params)

    def retrieve_unprocessed_episodes(self):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        episodes = []

        try:
            cursor.execute(
                """
                SELECT e.episode_number, 
                       e.file_name, 
                       e.is_processed, 
                       es.speaker_number, 
                       s.name AS speaker_name,
                       s.id AS speaker_id
                FROM episodes AS e
                JOIN episode_speakers AS es
                    ON e.episode_number = es.episode_id
                JOIN speakers AS s
                    ON s.id = es.speaker_id
                WHERE e.is_processed = false
                ORDER BY e.episode_number, es.speaker_number
                """
            )
            episodes = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()
        return episodes

    def store_embeddings(self, embeddings: List[dict], episode_id: int) -> None:
        """
        Store a list of embeddings with their associated segment data into the database.

        Args:
            embeddings: List of dictionaries containing 'speaker_id', 'text', and 'embedding' keys
            episode_id: The episode ID to associate with these embeddings
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for embedding_data in embeddings:
                cursor.execute(
                    "INSERT INTO transcript_segments (speaker_id, text, embedding, episode_id) VALUES (%s, %s, %s, %s)",
                    (
                        embedding_data["speaker_id"],
                        embedding_data["text"],
                        embedding_data["embedding"],
                        episode_id,
                    ),
                )
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing embeddings: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
