import logging
from typing import List, Dict, Any
from src.alerts.alert_model import Alert
from src.alerts.rules import RULES, ALERT_CONFIG, get_rule_by_id

logger = logging.getLogger(__name__)

class AlertEngine:
    """
    Evaluates frame analysis results against security rules and generates alerts.
    Maintains session state for tracking stateful rules like repeated vehicle visits.
    """
    def __init__(self):
        self.config = ALERT_CONFIG
        # State tracking: { "Location Name": { "vehicle description": count } }
        self.vehicle_history: Dict[str, Dict[str, int]] = {}

    def _track_vehicle(self, location: str, vehicle_desc: str) -> int:
        """Tracks the number of times a specific vehicle description is seen at a location."""
        desc_lower = vehicle_desc.lower()
        if location not in self.vehicle_history:
            self.vehicle_history[location] = {}
            
        self.vehicle_history[location][desc_lower] = self.vehicle_history[location].get(desc_lower, 0) + 1
        return self.vehicle_history[location][desc_lower]

    def _is_vehicle(self, description: str) -> bool:
        """Heuristic check if an object string describes a vehicle."""
        keywords = ['truck', 'car', 'vehicle', 'sedan', 'suv', 'van', 'pickup', 'motorcycle', 'f-150', 'f150']
        return any(kw in description.lower() for kw in keywords)

    def process_frame(self, frame_context: Any) -> List[Alert]:
        """
        Evaluates a single frame context against all security rules.
        Attaches generated alerts back to the context and returns them.
        """
        alerts: List[Alert] = []
        try:
            # Duck-typing extraction
            frame_id = getattr(frame_context, 'frame_id', -1)
            telemetry = getattr(frame_context, 'telemetry', {})
            analysis = getattr(frame_context, 'analysis_result', None)

            if not analysis:
                logger.debug(f"No analysis result for frame {frame_id}. Skipping alert generation.")
                return alerts

            loc = telemetry.get('location_name', 'Unknown')
            time_str = telemetry.get('timestamp', '00:00:00')
            is_night = telemetry.get('is_night', False)

            # Rule 1: NIGHT_PERSON_LOITERING
            if analysis.has_people and is_night:
                rule = get_rule_by_id("NIGHT_PERSON_LOITERING")
                alerts.append(Alert(
                    rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                    location_name=loc, severity_level=rule.severity_level,
                    alert_message=rule.alert_message_template.format(location=loc, time=time_str),
                    triggered_by="Person detected at night"
                ))

            # Rule 4: PERSON_IN_RESTRICTED_AREA
            if analysis.has_people:
                restricted = self.config.get("restricted_areas", [])
                if loc in restricted:
                    rule = get_rule_by_id("PERSON_IN_RESTRICTED_AREA")
                    alerts.append(Alert(
                        rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                        location_name=loc, severity_level=rule.severity_level,
                        alert_message=rule.alert_message_template.format(location=loc, time=time_str),
                        triggered_by="Person in restricted zone"
                    ))

            # Rule 6: MULTIPLE_PEOPLE_AT_GATE
            if analysis.person_count > 2 and loc == "Main Gate":
                rule = get_rule_by_id("MULTIPLE_PEOPLE_AT_GATE")
                alerts.append(Alert(
                    rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                    location_name=loc, severity_level=rule.severity_level,
                    alert_message=rule.alert_message_template.format(count=analysis.person_count, time=time_str),
                    triggered_by=f"{analysis.person_count} people detected"
                ))

            # Rule 7: SUSPICIOUS_ACTIVITY
            if analysis.is_suspicious:
                rule = get_rule_by_id("SUSPICIOUS_ACTIVITY")
                alerts.append(Alert(
                    rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                    location_name=loc, severity_level=rule.severity_level,
                    alert_message=rule.alert_message_template.format(activity=analysis.activity_description or "Suspicious behaviour", location=loc, time=time_str),
                    triggered_by=analysis.activity_description or "VLM explicit flag"
                ))

            # Vehicle Rules (2, 3, 5)
            if analysis.has_vehicles:
                auth_vehicles = [v.lower() for v in self.config.get("authorised_vehicles", [])]
                repeat_threshold = self.config.get("repeat_threshold", 3)
                
                # Rule 5: NIGHTTIME_VEHICLE
                if is_night:
                    rule = get_rule_by_id("NIGHTTIME_VEHICLE")
                    alerts.append(Alert(
                        rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                        location_name=loc, severity_level=rule.severity_level,
                        alert_message=rule.alert_message_template.format(object="Vehicle", location=loc, time=time_str),
                        triggered_by="Vehicle detected at night"
                    ))

                for obj in analysis.detected_objects:
                    if self._is_vehicle(obj):
                        obj_lower = obj.lower()
                        
                        # Rule 2: UNAUTHORISED_VEHICLE
                        is_auth = any(auth in obj_lower for auth in auth_vehicles)
                        if not is_auth:
                            rule = get_rule_by_id("UNAUTHORISED_VEHICLE")
                            alerts.append(Alert(
                                rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                                location_name=loc, severity_level=rule.severity_level,
                                alert_message=rule.alert_message_template.format(object=obj, location=loc, time=time_str),
                                triggered_by=obj
                            ))

                        # Rule 3: REPEATED_VEHICLE_VISIT
                        count = self._track_vehicle(loc, obj)
                        if count > repeat_threshold:
                            rule = get_rule_by_id("REPEATED_VEHICLE_VISIT")
                            alerts.append(Alert(
                                rule_id=rule.rule_id, frame_id=frame_id, timestamp=time_str,
                                location_name=loc, severity_level=rule.severity_level,
                                alert_message=rule.alert_message_template.format(object=obj, location=loc, time=time_str),
                                triggered_by=f"{obj} (Seen {count} times)"
                            ))

            # Attach alerts to context for downstream indexing
            setattr(frame_context, 'alerts', alerts)
            return alerts

        except Exception as e:
            logger.error(f"Alert generation failed for frame {getattr(frame_context, 'frame_id', 'Unknown')}: {e}")
            return alerts