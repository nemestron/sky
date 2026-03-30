import uuid
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Alert:
    """
    Structured representation of a triggered security alert.
    """
    rule_id: str
    frame_id: int
    timestamp: str
    location_name: str
    severity_level: str
    alert_message: str
    triggered_by: str
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")