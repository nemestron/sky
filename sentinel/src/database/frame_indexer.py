import json
import logging
from datetime import datetime, timezone
from typing import Any, List, Dict, Tuple
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class FrameIndexer:
    """
    Handles the serialization and transactional insertion of FrameContext objects
    into the SQLite database. Ensures cross-table transactional integrity.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _prepare_frame_data(self, frame_context: Any, alert_ids: List[str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Safely extracts and serialises data from a FrameContext object into database-ready formats.
        Converts booleans to integers and lists to JSON strings.
        """
        telemetry = getattr(frame_context, 'telemetry', {})
        timestamp = telemetry.get('timestamp', '')
        location_name = telemetry.get('location_name', '')
        latitude = float(telemetry.get('latitude', 0.0))
        longitude = float(telemetry.get('longitude', 0.0))
        altitude = float(telemetry.get('altitude_meters', 0.0))
        is_night = int(telemetry.get('is_night', False))
        
        analysis = getattr(frame_context, 'analysis_result', None)
        raw_vlm = getattr(analysis, 'raw_description', '') if analysis else ''
        activity = getattr(analysis, 'activity_description', '') if analysis else ''
        has_people = int(getattr(analysis, 'has_people', False)) if analysis else 0
        has_vehicles = int(getattr(analysis, 'has_vehicles', False)) if analysis else 0
        person_count = int(getattr(analysis, 'person_count', 0)) if analysis else 0
        is_suspicious = int(getattr(analysis, 'is_suspicious', False)) if analysis else 0
        
        vehicle_details = getattr(analysis, 'vehicle_details', []) if analysis else []
        vehicle_types = [v.get('type', 'unknown') for v in vehicle_details if isinstance(v, dict)]
        
        frame_record = {
            'frame_id': getattr(frame_context, 'frame_id', -1),
            'timestamp': timestamp,
            'location_name': location_name,
            'latitude': latitude,
            'longitude': longitude,
            'altitude_meters': altitude,
            'is_night': is_night,
            'frame_image_path': getattr(frame_context, 'image_path', ''),
            'raw_vlm_description': raw_vlm,
            'activity_description': activity,
            'has_people': has_people,
            'has_vehicles': has_vehicles,
            'vehicle_types_json': json.dumps(vehicle_types),
            'person_count': person_count,
            'is_suspicious': is_suspicious,
            'alert_ids_json': json.dumps(alert_ids),
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        detected_objects = []
        if analysis:
            for obj in getattr(analysis, 'detected_objects', []):
                detected_objects.append({
                    'frame_id': frame_record['frame_id'],
                    'object_type': 'general',
                    'object_colour': '',
                    'object_description': str(obj)
                })
            
            for veh in vehicle_details:
                detected_objects.append({
                    'frame_id': frame_record['frame_id'],
                    'object_type': veh.get('type', 'vehicle'),
                    'object_colour': veh.get('colour', ''),
                    'object_description': f"{veh.get('colour', '')} {veh.get('make_model', '')} {veh.get('type', '')}".strip()
                })

        return frame_record, detected_objects

    def index_frame(self, frame_context: Any, alert_ids: List[str]) -> None:
        """Indexes a single frame transactionally."""
        frame_record, detected_objects = self._prepare_frame_data(frame_context, alert_ids)
        self._execute_insert([frame_record], detected_objects)
        logger.debug(f"Successfully indexed frame {frame_record['frame_id']}")

    def bulk_index(self, frame_contexts: List[Tuple[Any, List[str]]]) -> None:
        """Indexes multiple frames in a single transaction for high-performance batch processing."""
        all_frames = []
        all_objects = []
        for fc, alerts in frame_contexts:
            f_rec, d_objs = self._prepare_frame_data(fc, alerts)
            all_frames.append(f_rec)
            all_objects.extend(d_objs)
        
        if all_frames:
            self._execute_insert(all_frames, all_objects)
            logger.info(f"Successfully bulk indexed {len(all_frames)} frames.")

    def _execute_insert(self, frames: List[Dict[str, Any]], objects: List[Dict[str, Any]]) -> None:
        """Executes the SQL insert operations within a managed transaction context."""
        frame_query = """
            INSERT OR REPLACE INTO frame_index (
                frame_id, timestamp, location_name, latitude, longitude, 
                altitude_meters, is_night, frame_image_path, raw_vlm_description, 
                activity_description, has_people, has_vehicles, vehicle_types_json, 
                person_count, is_suspicious, alert_ids_json, processing_timestamp
            ) VALUES (
                :frame_id, :timestamp, :location_name, :latitude, :longitude,
                :altitude_meters, :is_night, :frame_image_path, :raw_vlm_description,
                :activity_description, :has_people, :has_vehicles, :vehicle_types_json,
                :person_count, :is_suspicious, :alert_ids_json, :processing_timestamp
            )
        """
        
        object_query = """
            INSERT INTO detected_objects (
                frame_id, object_type, object_colour, object_description
            ) VALUES (
                :frame_id, :object_type, :object_colour, :object_description
            )
        """
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(frame_query, frames)
                if objects:
                    cursor.executemany(object_query, objects)
        except Exception as e:
            logger.error(f"Transaction failed during frame indexing: {e}")
            raise
