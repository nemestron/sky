import logging
from typing import Dict, Any, List
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class FrameQueryEngine:
    """
    Multi-criteria query interface for the frame index.
    Provides robust methods for filtering surveillance data across time, location,
    object types, and full-text AI descriptions.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns typed dictionaries."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {params}")
            return []

    def query_by_time_range(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """Returns frames within a specific ISO 8601 time range."""
        query = "SELECT * FROM frame_index WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
        return self._execute_query(query, (start_time, end_time))

    def query_by_object_type(self, object_type: str) -> List[Dict[str, Any]]:
        """Queries the normalized detected_objects table for specific entity types."""
        query = """
            SELECT DISTINCT f.* FROM frame_index f
            JOIN detected_objects d ON f.frame_id = d.frame_id
            WHERE d.object_type LIKE ? OR d.object_description LIKE ?
            ORDER BY f.timestamp
        """
        search_term = f"%{object_type}%"
        return self._execute_query(query, (search_term, search_term))

    def query_by_location(self, location_name: str) -> List[Dict[str, Any]]:
        """Returns all frames captured at a given location."""
        query = "SELECT * FROM frame_index WHERE location_name = ? ORDER BY timestamp"
        return self._execute_query(query, (location_name,))

    def query_by_alert_status(self, has_alert: bool) -> List[Dict[str, Any]]:
        """Filters frames based on whether they triggered any security alerts."""
        if has_alert:
            query = "SELECT * FROM frame_index WHERE alert_ids_json != '[]' AND alert_ids_json IS NOT NULL ORDER BY timestamp"
        else:
            query = "SELECT * FROM frame_index WHERE alert_ids_json = '[]' OR alert_ids_json IS NULL ORDER BY timestamp"
        return self._execute_query(query)

    def query_by_night(self, is_night: bool) -> List[Dict[str, Any]]:
        """Filters frames by day or night context."""
        query = "SELECT * FROM frame_index WHERE is_night = ? ORDER BY timestamp"
        return self._execute_query(query, (1 if is_night else 0,))

    def full_text_search(self, search_term: str) -> List[Dict[str, Any]]:
        """Utilizes SQLite FTS5 for high-performance free-text search on VLM descriptions."""
        query = """
            SELECT f.* FROM frame_index f
            JOIN vlm_search v ON f.frame_id = v.rowid
            WHERE vlm_search MATCH ?
            ORDER BY rank
        """
        # Enclose in quotes to handle multi-word searches gracefully in FTS5
        fts_term = f'"{search_term}"'
        return self._execute_query(query, (fts_term,))

    def combined_query(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Dynamically constructs a safe, parameterized query using multiple filter criteria.
        Accepted kwargs: object_type, start_time, end_time, location_name, is_night.
        """
        base_query = "SELECT DISTINCT f.* FROM frame_index f "
        joins = []
        where_clauses = []
        params = []

        if 'object_type' in kwargs and kwargs['object_type']:
            joins.append("JOIN detected_objects d ON f.frame_id = d.frame_id")
            where_clauses.append("(d.object_type LIKE ? OR d.object_description LIKE ?)")
            term = f"%{kwargs['object_type']}%"
            params.extend([term, term])

        if 'start_time' in kwargs and 'end_time' in kwargs:
            where_clauses.append("f.timestamp BETWEEN ? AND ?")
            params.extend([kwargs['start_time'], kwargs['end_time']])

        if 'location_name' in kwargs and kwargs['location_name']:
            where_clauses.append("f.location_name = ?")
            params.append(kwargs['location_name'])

        if 'is_night' in kwargs and kwargs['is_night'] is not None:
            where_clauses.append("f.is_night = ?")
            params.append(1 if kwargs['is_night'] else 0)

        query = base_query + " ".join(joins)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY f.timestamp"

        return self._execute_query(query, tuple(params))
