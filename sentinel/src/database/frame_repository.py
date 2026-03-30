import logging
from typing import Dict, Any, Optional
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class FrameRepository:
    """
    Base Query layer for the frame_index and detected_objects tables.
    Provides fundamental read access, to be expanded upon by the multi-criteria query engine.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_frame_by_id(self, frame_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single complete frame record by its ID."""
        query = "SELECT * FROM frame_index WHERE frame_id = ?"
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (frame_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving frame {frame_id}: {e}")
            return None
