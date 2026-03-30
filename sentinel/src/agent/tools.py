import os
import json
from langchain.tools import tool
from src.database.query_engine import FrameQueryEngine
from src.database.alert_repository import AlertRepository
from src.database.result_formatter import QueryResultFormatter

# Initialize database interfaces
query_engine = FrameQueryEngine()
alert_repo = AlertRepository()
formatter = QueryResultFormatter()

@tool
def SearchByObjectTool(object_type: str) -> str:
    """
    Use this tool when the user asks about a specific type of vehicle, person, or object detected in the surveillance footage.
    Input should be a string representing the object type (e.g., 'truck', 'person', 'car').
    Returns a formatted list of matching frames with timestamps and locations.
    """
    try:
        results = query_engine.query_by_object_type(object_type)
        return formatter.format_frame_records(results)
    except Exception as e:
        return f"Error executing SearchByObjectTool: {str(e)}"

@tool
def SearchByTimeTool(time_range: str) -> str:
    """
    Use this tool when the user asks about events occurring within a specific time range.
    Input should be a comma-separated string formatted as 'HH:MM,HH:MM' representing the start and end times.
    Returns the frame count and summary for that specified period.
    """
    try:
        parts = time_range.split(',')
        if len(parts) != 2:
            return "Error: Input must be exactly two times separated by a comma (e.g., '10:00,14:00')."
        
        start_time, end_time = parts[0].strip(), parts[1].strip()
        results = query_engine.query_by_time_range(start_time, end_time)
        return formatter.format_time_summary(results)
    except Exception as e:
        return f"Error executing SearchByTimeTool: {str(e)}"

@tool
def SearchByLocationTool(location_name: str) -> str:
    """
    Use this tool when the user asks about activity, events, or objects at a specific location.
    Input should be the exact location name string (e.g., 'Main Gate', 'Garage', 'Parking Lot').
    Returns a summary of all indexed events at that specific location.
    """
    try:
        results = query_engine.query_by_location(location_name)
        return formatter.format_frame_records(results)
    except Exception as e:
        return f"Error executing SearchByLocationTool: {str(e)}"

@tool
def GetAlertsTool(severity: str = "") -> str:
    """
    Use this tool when the user asks about security alerts, violations, rules triggered, or suspicious activity.
    Input is an optional severity level string ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'). If no specific severity is requested, pass an empty string.
    Returns a formatted list of security alerts.
    """
    try:
        severity_clean = severity.strip().upper()
        if severity_clean in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            alerts = alert_repo.get_alerts_by_severity(severity_clean)
        else:
            alerts = alert_repo.get_all_alerts()
        return formatter.format_alerts(alerts)
    except Exception as e:
        return f"Error executing GetAlertsTool: {str(e)}"

@tool
def FullTextSearchTool(search_term: str) -> str:
    """
    Use this tool when the user searches for complex descriptions, specific actions, or free-text queries not covered by simple object or location searches.
    Input should be a free-text search term string (e.g., 'person running', 'blue truck parked').
    Returns matching frame descriptions from the full-text database index.
    """
    try:
        results = query_engine.full_text_search(search_term)
        return formatter.format_frame_records(results)
    except Exception as e:
        return f"Error executing FullTextSearchTool: {str(e)}"

@tool
def GetVideoSummaryTool(dummy_input: str = "") -> str:
    """
    Use this tool when the user asks for a general summary, overview, or final report of the entire 24-hour surveillance session.
    Input should be an empty string.
    Returns a concise paragraph summarizing the entire session.
    """
    try:
        # Resolve the path to the session summary JSON file in the data directory
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        summary_file = os.path.join(base_path, 'data', 'session_summary.json')
        
        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('summary', 'Summary data is empty.')
        else:
            return "Video summary has not been generated yet. The session must be fully processed first."
    except Exception as e:
        return f"Error executing GetVideoSummaryTool: {str(e)}"

# Export all tools as a list for easy agent initialization
AGENT_TOOLS = [
    SearchByObjectTool,
    SearchByTimeTool,
    SearchByLocationTool,
    GetAlertsTool,
    FullTextSearchTool,
    GetVideoSummaryTool
]