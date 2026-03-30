import uuid
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LogGenerator:
    """
    Generates structured and human-readable log entries from AnalysisResult 
    and telemetry context.
    """

    @staticmethod
    def generate_logs(frame_context: Any) -> List[Dict[str, Any]]:
        """
        Takes a FrameContext (with attached analysis_result and telemetry)
        and produces a list of structured log dictionaries.
        """
        logs = []
        try:
            # Duck-typing extraction to maintain loose coupling
            frame_id = getattr(frame_context, 'frame_id', -1)
            telemetry = getattr(frame_context, 'telemetry', {})
            analysis = getattr(frame_context, 'analysis_result', None)

            if not analysis:
                logger.warning(f"No analysis result found for frame {frame_id}. Skipping log generation.")
                return logs

            location_name = telemetry.get('location_name', 'Unknown Location')
            raw_timestamp = telemetry.get('timestamp', '00:00:00')
            is_night = telemetry.get('is_night', False)

            # Extract HH:MM from ISO 8601 timestamp string
            try:
                # Handle basic ISO string parsing safely
                dt_obj = datetime.fromisoformat(raw_timestamp.replace('Z', '+00:00'))
                time_str = dt_obj.strftime('%H:%M')
            except ValueError:
                # Fallback if timestamp format is unexpected
                time_str = raw_timestamp[11:16] if len(raw_timestamp) >= 16 else raw_timestamp[:5]

            night_suffix = " (night)" if is_night else ""

            # Base log template dictionary
            base_log = {
                "frame_id": frame_id,
                "timestamp": raw_timestamp,
                "location_name": location_name,
                "is_night": is_night,
                "object_description": None,
                "activity_description": None,
                "log_text": ""
            }

            # 1. Handle Empty Scenes
            if not analysis.detected_objects and not analysis.activity_description:
                empty_log = base_log.copy()
                empty_log["log_id"] = str(uuid.uuid4())
                empty_log["log_text"] = f"No activity detected at {location_name}, {time_str}{night_suffix}."
                logs.append(empty_log)
                return logs

            # 2. Handle Detected Objects
            for obj in analysis.detected_objects:
                obj_log = base_log.copy()
                obj_log["log_id"] = str(uuid.uuid4())
                obj_log["object_description"] = obj
                obj_log["log_text"] = f"{obj.capitalize()} spotted at {location_name}, {time_str}{night_suffix}."
                logs.append(obj_log)

            # 3. Handle Activity Descriptions
            if analysis.activity_description and analysis.activity_description.lower() not in ['none', 'n/a', '']:
                act_log = base_log.copy()
                act_log["log_id"] = str(uuid.uuid4())
                act_log["activity_description"] = analysis.activity_description
                act_log["log_text"] = f"{analysis.activity_description.capitalize()} observed at {location_name}, {time_str}{night_suffix}."
                logs.append(act_log)

            return logs

        except Exception as e:
            logger.error(f"Error generating logs for frame {getattr(frame_context, 'frame_id', 'Unknown')}: {str(e)}")
            return logs