import json
from typing import List, Dict, Any

class QueryResultFormatter:
    """
    Transforms raw database dictionary records into human-readable text summaries.
    This is critical for providing clean context to the LangChain conversational agent.
    """
    
    @staticmethod
    def format_to_text(records: List[Dict[str, Any]]) -> str:
        """Converts a list of frame records into a readable string summary."""
        if not records:
            return "No matching records found."
        
        summary_lines = [f"Found {len(records)} matching events:"]
        
        for idx, record in enumerate(records, 1):
            timestamp = record.get('timestamp', 'Unknown Time')
            location = record.get('location_name', 'Unknown Location')
            activity = record.get('activity_description', '')
            
            # Format vehicles
            vehicles = []
            try:
                vehicles = json.loads(record.get('vehicle_types_json', '[]'))
            except (TypeError, json.JSONDecodeError):
                pass
            
            vehicle_str = f"Vehicles: {', '.join(vehicles)}" if vehicles else "No vehicles"
            
            # Format people
            people_cnt = record.get('person_count', 0)
            people_str = f"People: {people_cnt}" if people_cnt > 0 else "No people"
            
            # Format alerts
            alerts = []
            try:
                alerts = json.loads(record.get('alert_ids_json', '[]'))
            except (TypeError, json.JSONDecodeError):
                pass
            
            alert_str = " | [ALERT TRIGGERED]" if alerts else ""
            
            line = f"{idx}. [{timestamp}] {location}: {activity} ({vehicle_str}, {people_str}){alert_str}"
            summary_lines.append(line)
            
        return "\n".join(summary_lines)
