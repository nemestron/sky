import sqlite3
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sentinel.db')

class DatabaseManager:
    """
    Manages SQLite database connections safely using context managers.
    """
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Yields a database connection and ensures it is closed after use."""
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        # Configure row factory to return rows as dictionaries
        conn.row_factory = sqlite3.Row 
        try:
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def init_db():
        """Initializes the database schema for the alerts table."""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        try:
            with DatabaseManager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id TEXT PRIMARY KEY,
                        rule_id TEXT,
                        frame_id INTEGER,
                        timestamp TEXT,
                        location_name TEXT,
                        severity_level TEXT,
                        alert_message TEXT,
                        triggered_by TEXT,
                        is_resolved INTEGER,
                        created_at TEXT
                    )
                ''')
                conn.commit()
                logger.info("Database schema (alerts) initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
            raise