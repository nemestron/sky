from dataclasses import dataclass

@dataclass
class TelemetryRecord:
    \"\"\"
    Strict data schema for simulated drone telemetry.
    Acts as the contract between the telemetry module and all consumers.
    \"\"\"
    frame_id: int
    timestamp: str
    latitude: float
    longitude: float
    altitude_meters: float
    location_name: str
    drone_heading: float
    is_night: bool
