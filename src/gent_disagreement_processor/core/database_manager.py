import logging
import os
from typing import List, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


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

    def get_connection(self):
        """
        Create and return a database connection.
        """
        return psycopg2.connect(**self.connection_params)

    def store_embeddings(self, embeddings: List[dict], episode_id: int) -> None:
        """
        Store a list of embeddings with their associated segment data into the database.

        Args:
            embeddings: List of dictionaries containing 'speaker', 'text', and 'embedding' keys
            episode_id: The episode ID to associate with these embeddings
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for embedding_data in embeddings:
                cursor.execute(
                    "INSERT INTO transcript_segments (speaker, text, embedding, episode_id) VALUES (%s, %s, %s, %s)",
                    (
                        embedding_data["speaker"],
                        embedding_data["text"],
                        embedding_data["embedding"],
                        episode_id,
                    ),
                )
            conn.commit()
            self.logger.info(f"Stored {len(embeddings)} embeddings successfully!")
        except Exception as e:
            self.logger.error(f"Error storing embeddings: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[dict]:
        """
        Execute a query with optional parameters.
        """
        cursor = None
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
