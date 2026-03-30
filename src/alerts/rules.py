from dataclasses import dataclass
from typing import Dict

@dataclass
class SecurityRule:
    """
    Data structure defining a security rule to be evaluated by the Alert Engine.
    """
    rule_id: str
    rule_name: str
    description: str
    trigger_condition: str
    severity_level: str
    alert_message_template: str

# Predefined security rules mapping
RULES: Dict[str, SecurityRule] = {
    "NIGHT_PERSON_LOITERING": SecurityRule(
        rule_id="NIGHT_PERSON_LOITERING",
        rule_name="Night Person Loitering",
        description="Fires when a person is detected during night hours.",
        trigger_condition="has_people=True AND is_night=True",
        severity_level="HIGH",
        alert_message_template="Person loitering at {location}, {time}."
    ),
    "UNAUTHORISED_VEHICLE": SecurityRule(
        rule_id="UNAUTHORISED_VEHICLE",
        rule_name="Unauthorised Vehicle",
        description="Fires when a detected vehicle is not in the authorised vehicles list.",
        trigger_condition="has_vehicles=True AND vehicle not in authorised_vehicles",
        severity_level="MEDIUM",
        alert_message_template="Unauthorised vehicle detected at {location}, {time}."
    ),
    "REPEATED_VEHICLE_VISIT": SecurityRule(
        rule_id="REPEATED_VEHICLE_VISIT",
        rule_name="Repeated Vehicle Visit",
        description="Fires when the same vehicle is detected at the same location beyond the allowed threshold.",
        trigger_condition="vehicle seen > repeat_threshold at same location",
        severity_level="LOW",
        alert_message_template="Vehicle seen multiple times at {location}, {time}."
    ),
    "PERSON_IN_RESTRICTED_AREA": SecurityRule(
        rule_id="PERSON_IN_RESTRICTED_AREA",
        rule_name="Person in Restricted Area",
        description="Fires when a person is detected in a configured restricted area.",
        trigger_condition="has_people=True AND location_name in restricted_areas",
        severity_level="CRITICAL",
        alert_message_template="Person detected in restricted area ({location}) at {time}."
    ),
    "NIGHTTIME_VEHICLE": SecurityRule(
        rule_id="NIGHTTIME_VEHICLE",
        rule_name="Nighttime Vehicle",
        description="Fires when any vehicle is detected during night hours.",
        trigger_condition="has_vehicles=True AND is_night=True",
        severity_level="MEDIUM",
        alert_message_template="Vehicle detected at night at {location}, {time}."
    ),
    "MULTIPLE_PEOPLE_AT_GATE": SecurityRule(
        rule_id="MULTIPLE_PEOPLE_AT_GATE",
        rule_name="Multiple People at Gate",
        description="Fires when more than two people are detected at the Main Gate.",
        trigger_condition="person_count > 2 AND location_name == 'Main Gate'",
        severity_level="MEDIUM",
        alert_message_template="Multiple people detected at {location}, {time}."
    ),
    "SUSPICIOUS_ACTIVITY": SecurityRule(
        rule_id="SUSPICIOUS_ACTIVITY",
        rule_name="Suspicious Activity",
        description="Fires when the VLM explicitly flags the activity as suspicious.",
        trigger_condition="is_suspicious=True",
        severity_level="HIGH",
        alert_message_template="Suspicious activity detected at {location}, {time}."
    )
}

def get_all_rules() -> Dict[str, SecurityRule]:
    """Returns the dictionary of all defined security rules."""
    return RULES
# ---------------------------------------------------------
# DEPENDENCY PATCH: INJECTED TO RESOLVE IMPORT ERRORS
# ---------------------------------------------------------
import json
import os

try:
    _config_path = os.path.join(os.path.dirname(__file__), 'alert_config.json')
    if os.path.exists(_config_path):
        with open(_config_path, 'r') as _f:
            ALERT_CONFIG = json.load(_f)
    else:
        # Fallback default configuration if JSON is missing
        ALERT_CONFIG = {
            'authorised_vehicles': [],
            'restricted_areas': ['North Perimeter', 'Server Room'],
            'repeat_threshold': 3
        }
except Exception:
    ALERT_CONFIG = {}
# ---------------------------------------------------------
# DEPENDENCY PATCH: HELPER FUNCTIONS FOR ALERT ENGINE
# ---------------------------------------------------------
def get_all_rules():
    'Returns all defined rules. Assumes rules are stored in a list named RULES.'
    return globals().get('RULES', [])

def get_rule_by_id(rule_id):
    'Fetches a specific rule by its ID.'
    rules = get_all_rules()
    for r in rules:
        if isinstance(r, dict) and r.get('rule_id') == rule_id:
            return r
        elif hasattr(r, 'rule_id') and getattr(r, 'rule_id') == rule_id:
            return r
    return None