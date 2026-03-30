import logging
from typing import List
from src.database.db_manager import DatabaseManager
from src.alerts.alert_model import Alert

logger = logging.getLogger(__name__)

class AlertRepository:
    """
    CRUD operations strictly for the alerts table.
    """

    @staticmethod
    def insert_alert(alert: Alert) -> None:
        """Inserts a new Alert object into the database."""
        try:
            with DatabaseManager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO alerts (
                        alert_id, rule_id, frame_id, timestamp, location_name, 
                        severity_level, alert_message, triggered_by, is_resolved, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id, alert.rule_id, alert.frame_id, alert.timestamp,
                    alert.location_name, alert.severity_level, alert.alert_message,
                    alert.triggered_by, 1 if alert.is_resolved else 0, alert.created_at
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert alert {alert.alert_id}: {e}")

    @staticmethod
    def _row_to_alert(row) -> Alert:
        """Helper to map a sqlite3.Row to an Alert dataclass."""
        return Alert(
            alert_id=row['alert_id'],
            rule_id=row['rule_id'],
            frame_id=row['frame_id'],
            timestamp=row['timestamp'],
            location_name=row['location_name'],
            severity_level=row['severity_level'],
            alert_message=row['alert_message'],
            triggered_by=row['triggered_by'],
            is_resolved=bool(row['is_resolved']),
            created_at=row['created_at']
        )

    @staticmethod
    def get_all_alerts() -> List[Alert]:
        """Retrieves all alerts."""
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts ORDER BY created_at DESC')
            return [AlertRepository._row_to_alert(row) for row in cursor.fetchall()]

    @staticmethod
    def get_alerts_by_severity(severity: str) -> List[Alert]:
        """Retrieves alerts filtered by severity level."""
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE severity_level = ? ORDER BY created_at DESC', (severity,))
            return [AlertRepository._row_to_alert(row) for row in cursor.fetchall()]

    @staticmethod
    def get_alerts_by_location(location: str) -> List[Alert]:
        """Retrieves alerts filtered by location name."""
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE location_name = ? ORDER BY created_at DESC', (location,))
            return [AlertRepository._row_to_alert(row) for row in cursor.fetchall()]

    @staticmethod
    def get_alerts_by_timerange(start: str, end: str) -> List[Alert]:
        """Retrieves alerts within a specific time window."""
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp ASC', (start, end))
            return [AlertRepository._row_to_alert(row) for row in cursor.fetchall()]

    @staticmethod
    def get_alerts_for_frame(frame_id: int) -> List[Alert]:
        """Retrieves alerts triggered by a specific frame ID."""
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE frame_id = ? ORDER BY created_at ASC', (frame_id,))
            return [AlertRepository._row_to_alert(row) for row in cursor.fetchall()]

    @staticmethod
    def mark_resolved(alert_id: str) -> None:
        """Marks an alert as resolved in the database."""
        try:
            with DatabaseManager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE alerts SET is_resolved = 1 WHERE alert_id = ?', (alert_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")