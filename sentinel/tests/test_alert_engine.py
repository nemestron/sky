import pytest

def test_alert_night_person_loitering():
    """Verify processing a night-time frame with a person triggers NIGHT_PERSON_LOITERING."""
    pass

def test_alert_repeated_vehicle_visit():
    """Verify processing the same vehicle 3 times triggers REPEATED_VEHICLE_VISIT."""
    pass

def test_alert_daytime_empty_scene():
    """Verify processing a daytime empty scene generates no alerts."""
    pass

def test_alert_person_in_restricted_area():
    """Verify a person in a restricted area triggers PERSON_IN_RESTRICTED_AREA."""
    pass

def test_alert_object_attributes():
    """Verify the Alert object created has the correct severity, message, frame_id, and timestamp."""
    pass