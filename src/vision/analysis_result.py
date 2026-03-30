from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AnalysisResult:
    """
    Structured representation of the VLM analysis output.
    This standardized format is consumed by the Alert Engine and Database Indexer.
    """
    raw_description: str
    detected_objects: List[str] = field(default_factory=list)
    activity_description: str = ""
    has_people: bool = False
    has_vehicles: bool = False
    vehicle_details: List[Dict[str, str]] = field(default_factory=list)
    person_count: int = 0
    is_suspicious: bool = False