import json
from pathlib import Path

# Dynamically resolve absolute path to data directory
BASE_DIR = Path(__file__).parent.parent.parent
SIMULATION_FILE = BASE_DIR / "data" / "simulated_frames.json"

class SimulationAdapter:
    """
    Adapter module that presents text descriptions as if they came from the VLM.
    Enables end-to-end testing of the pipeline without making Gemini API calls.
    """
    def __init__(self, simulation_file_path=SIMULATION_FILE):
        self.simulation_file_path = Path(simulation_file_path)
        self.simulated_data = self._load_data()

    def _load_data(self):
        """Loads the simulated frames JSON file."""
        if not self.simulation_file_path.exists():
            print(f"Warning: Simulation file not found at {self.simulation_file_path}")
            return {}
            
        try:
            with open(self.simulation_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding simulation JSON: {e}")
            return {}

    def get_frame_description(self, frame_id: int) -> str:
        """
        Retrieves the text description for a given frame ID.
        If the exact frame ID is not mapped, returns a default authentic scene description.
        """
        frame_key = str(frame_id)
        
        # Default description aligned with the authentic baseline of the video
        default_description = "Overhead view of the parking lot. Continuing activity from previous frames."
        
        return self.simulated_data.get(frame_key, default_description)

if __name__ == "__main__":
    adapter = SimulationAdapter()
    print("Testing Simulation Adapter with authentic frame data...")
    print(f"Frame 0: {adapter.get_frame_description(0)}")
    print(f"Frame 90: {adapter.get_frame_description(90)}")
    print(f"Frame 15: (Unmapped fallback): {adapter.get_frame_description(15)}")