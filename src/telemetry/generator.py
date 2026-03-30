import json
import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Dynamically resolve absolute paths to ensure reliability
TELEMETRY_DIR = Path(__file__).parent
BASE_DIR = TELEMETRY_DIR.parent.parent
sys.path.append(str(BASE_DIR))

# Import the single source of truth for frame counts
from src.utils.config import EXPECTED_FRAME_COUNT

DATA_DIR = BASE_DIR / "data"
LOCATIONS_FILE = TELEMETRY_DIR / "locations.json"

def load_locations():
    """Loads the predefined location vocabulary and coordinates."""
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_telemetry(simulation_date_str="2024-01-15", total_frames=EXPECTED_FRAME_COUNT):
    """
    Generates synthetic drone telemetry for a monitoring cycle.
    Distributes the frames evenly across a 24-hour period.
    """
    locations = load_locations()
    location_names = list(locations.keys())
    
    start_time = datetime.strptime(simulation_date_str, "%Y-%m-%d")
    
    # Calculate seconds between each frame to span 24 hours
    time_step_seconds = (24 * 3600) / total_frames if total_frames > 1 else 0
    
    telemetry_data = []
    
    for frame_id in range(total_frames):
        current_time = start_time + timedelta(seconds=frame_id * time_step_seconds)
        
        # Cycle through locations sequentially
        loc_index = int((frame_id / total_frames) * len(location_names))
        if loc_index >= len(location_names):
            loc_index = len(location_names) - 1
            
        loc_name = location_names[loc_index]
        base_loc = locations[loc_name]
        
        # Add slight variation to simulate drone hover/movement
        lat = base_loc["latitude"] + random.uniform(-0.0002, 0.0002)
        lon = base_loc["longitude"] + random.uniform(-0.0002, 0.0002)
        
        altitude = random.uniform(5.0, 20.0)
        heading = random.uniform(0.0, 360.0)
        
        # Rule: is_night is True if hour is >= 22 or < 6
        is_night = current_time.hour >= 22 or current_time.hour < 6
        
        record = {
            "frame_id": frame_id,
            "timestamp": current_time.isoformat(),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude_meters": round(altitude, 2),
            "location_name": loc_name,
            "drone_heading": round(heading, 2),
            "is_night": is_night
        }
        
        telemetry_data.append(record)
        
    return telemetry_data

def save_telemetry_to_disk(telemetry_data):
    """Saves the generated telemetry to CSV and JSON formats in the data directory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_file = DATA_DIR / "telemetry_data.csv"
    json_file = DATA_DIR / "telemetry_data.json"
    
    # Save as JSON
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(telemetry_data, file, indent=4)
        
    # Save as CSV
    if telemetry_data:
        keys = telemetry_data[0].keys()
        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(telemetry_data)
            
    return csv_file, json_file

if __name__ == "__main__":
    print("Generating simulated telemetry dataset...")
    data = generate_telemetry(total_frames=EXPECTED_FRAME_COUNT)
    csv_path, json_path = save_telemetry_to_disk(data)
    
    print(f"Success. Generated {len(data)} telemetry records.")
    print(f"CSV saved to: {csv_path}")
    print(f"JSON saved to: {json_path}")