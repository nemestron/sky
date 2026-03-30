import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from .schema import get_all_schema_statements

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages SQLite database connections and schema initialisation.
    Implements WAL mode for concurrent read/write operations.
    """
    def __init__(self, db_path: str | Path = "data/sentinel.db"):
        self.db_path = Path(db_path)
        self._initialise_database()

    def _initialise_database(self) -> None:
        """Executes all schema definitions to ensure tables and triggers exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for statement in get_all_schema_statements():
                    cursor.execute(statement)
                conn.commit()
            logger.info("Database schema initialised successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialise database schema: {e}")
            raise

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Provides a transactional, thread-safe database connection.
        Yields a connection that automatically commits on success or rolls back on failure.
        """
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False
        )
        
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Enable Write-Ahead Logging for concurrent Streamlit UI access during processing
        conn.execute("PRAGMA journal_mode=WAL;")
        
        # Return rows as dictionary-like objects for easier data mapping
        conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction rolled back due to error: {e}")
            raise
        finally:
            conn.close()
