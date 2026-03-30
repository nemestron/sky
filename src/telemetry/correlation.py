import csv
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

# Dynamically resolve absolute paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
FRAMES_DIR = BASE_DIR / "frames"
TELEMETRY_CSV = DATA_DIR / "telemetry_data.csv"

@dataclass
class FrameContext:
    """
    Unified data structure linking a physical frame to its spatial telemetry
    and acting as a carrier for downstream VLM analysis.
    """
    frame_id: int
    image_path: str
    telemetry: Dict[str, Any]
    vlm_analysis: Optional[Dict[str, Any]] = None

class CorrelationEngine:
    """
    Validates and merges extracted frames with their corresponding telemetry records.
    """
    def __init__(self, telemetry_file=TELEMETRY_CSV, frames_dir=FRAMES_DIR):
        self.telemetry_file = Path(telemetry_file)
        self.frames_dir = Path(frames_dir)

    def load_telemetry(self) -> Dict[int, Dict[str, Any]]:
        """Loads telemetry data from CSV into a dictionary keyed by frame_id."""
        if not self.telemetry_file.exists():
            raise FileNotFoundError(f"Telemetry file not found: {self.telemetry_file}")

        telemetry_dict = {}
        with open(self.telemetry_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert string frame_id to integer for strict matching
                frame_id = int(row["frame_id"])
                
                # Type cast boolean and float values
                row["frame_id"] = frame_id
                row["latitude"] = float(row["latitude"])
                row["longitude"] = float(row["longitude"])
                row["altitude_meters"] = float(row["altitude_meters"])
                row["drone_heading"] = float(row["drone_heading"])
                row["is_night"] = row["is_night"] == "True"
                
                telemetry_dict[frame_id] = row
                
        return telemetry_dict

    def get_frame_files(self) -> Dict[int, Path]:
        """Scans the frames directory and returns a dictionary of valid frame paths keyed by frame_id."""
        if not self.frames_dir.exists():
            raise FileNotFoundError(f"Frames directory not found: {self.frames_dir}")

        frame_files = {}
        # Matches files like frame_00000.jpg
        for file_path in self.frames_dir.glob("frame_*.jpg"):
            try:
                # Extract integer ID from filename (e.g., 'frame_00042.jpg' -> 42)
                frame_id_str = file_path.stem.split("_")[1]
                frame_id = int(frame_id_str)
                frame_files[frame_id] = file_path
            except (IndexError, ValueError):
                print(f"Warning: Ignored irregularly named file in frames directory: {file_path.name}")
                
        return frame_files

    def correlate(self) -> List[FrameContext]:
        """
        Executes the correlation process. 
        Enforces a strict 1:1 mapping between telemetry records and extracted frames.
        """
        telemetry_data = self.load_telemetry()
        frame_files = self.get_frame_files()

        telemetry_keys = set(telemetry_data.keys())
        frame_keys = set(frame_files.keys())

        # Strict Validation Phase
        if telemetry_keys != frame_keys:
            missing_frames = telemetry_keys - frame_keys
            missing_telemetry = frame_keys - telemetry_keys
            
            error_msg = "CRITICAL ALIGNMENT ERROR: Telemetry and Frames do not strictly match 1:1.\n"
            if missing_frames:
                error_msg += f"- Missing {len(missing_frames)} image files for existing telemetry records.\n"
            if missing_telemetry:
                error_msg += f"- Missing {len(missing_telemetry)} telemetry records for existing image files.\n"
            
            raise ValueError(error_msg)

        # Merge Phase
        correlated_contexts = []
        for frame_id in sorted(telemetry_keys):
            context = FrameContext(
                frame_id=frame_id,
                image_path=str(frame_files[frame_id]),
                telemetry=telemetry_data[frame_id]
            )
            correlated_contexts.append(context)

        return correlated_contexts

if __name__ == "__main__":
    print("Initializing Correlation Engine...")
    try:
        engine = CorrelationEngine()
        contexts = engine.correlate()
        print(f"SUCCESS: Perfectly correlated {len(contexts)} frame contexts.")
        
        # Display sample verification
        sample = contexts[0]
        print("\nSample Context Verification (Frame 0):")
        print(f"- Image Path: {sample.image_path}")
        print(f"- Location: {sample.telemetry['location_name']}")
        print(f"- Coordinates: {sample.telemetry['latitude']}, {sample.telemetry['longitude']}")
        print(f"- Is Night: {sample.telemetry['is_night']}")
        
    except Exception as e:
        print(f"\nCORRELATION FAILED:\n{str(e)}")
        sys.exit(1)