import logging
import json
import os
from typing import List, Any, Dict
from PIL import Image

from src.vision.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class FrameAnalysisPipeline:
    """
    Central orchestrator for frame analysis.
    Iterates through FrameContext objects, fetches VLM descriptions,
    and attaches the raw output back to the context.
    """
    
    def __init__(self, use_simulation: bool = False, simulation_data_path: str = "data/simulated_frames.json"):
        """
        Initializes the pipeline.
        If use_simulation is True, API calls are bypassed and local text descriptions are used.
        """
        self.use_simulation = use_simulation
        self.simulation_data_path = simulation_data_path
        self.gemini_client = None if use_simulation else GeminiClient()
        self.simulation_data = {}

        if self.use_simulation:
            self._load_simulation_data()

    def _load_simulation_data(self) -> None:
        """Loads fallback text descriptions from a JSON file."""
        try:
            if os.path.exists(self.simulation_data_path):
                with open(self.simulation_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.simulation_data = {str(k): v for k, v in data.items()}
                logger.info("Loaded simulation data successfully.")
            else:
                logger.warning(f"Simulation data file not found at {self.simulation_data_path}")
        except Exception as e:
            logger.error(f"Failed to load simulation data: {str(e)}")

    def _build_context_prompt(self, telemetry: Dict[str, Any]) -> str:
        """
        Generates a grounding prompt using telemetry data to guide the VLM 
        toward security-relevant context.
        """
        time_str = telemetry.get('timestamp', 'Unknown Time')
        loc_str = telemetry.get('location_name', 'Unknown Location')
        alt = telemetry.get('altitude_meters', 0.0)
        is_night = telemetry.get('is_night', False)
        
        environment = "Nighttime" if is_night else "Daytime"
        return f"Context: Location is {loc_str}. Time is {time_str} ({environment}). Drone altitude is {alt}m."

    def process_frames(self, frame_contexts: List[Any]) -> List[Any]:
        """
        Processes a list of FrameContext objects.
        For each frame, sends data to the VLM (or simulator) and attaches the raw response.
        """
        total_frames = len(frame_contexts)
        logger.info(f"Starting analysis pipeline for {total_frames} frames. Mode: {'Simulation' if self.use_simulation else 'Real API'}")

        for index, context in enumerate(frame_contexts):
            # Duck-typing access to accommodate Phase 2 correlation structures
            frame_id = getattr(context, 'frame_id', 'Unknown')
            
            # Progress indicator required by specifications
            print(f"Analysing frame {index + 1}/{total_frames} (Frame ID: {frame_id})...")

            telemetry = getattr(context, 'telemetry', {})
            context_prompt = self._build_context_prompt(telemetry)
            
            raw_response = ""

            if self.use_simulation:
                raw_response = self.simulation_data.get(str(frame_id), "Simulation output: No specific activity observed.")
            else:
                image_path = getattr(context, 'image_path', None)
                if image_path and os.path.exists(image_path):
                    try:
                        with Image.open(image_path) as img:
                            raw_response = self.gemini_client.send_frame_for_analysis(img, context_prompt)
                    except Exception as e:
                        logger.error(f"Frame {frame_id} processing failed: {str(e)}")
                        raw_response = "ERROR: Failed to process image file."
                else:
                    logger.warning(f"Image path missing or invalid for frame {frame_id}: {image_path}")
                    raw_response = "ERROR: Image file not found."

            # Attach the raw text to the context for downstream parsing
            setattr(context, 'raw_vlm_analysis', raw_response)

        logger.info("Frame analysis pipeline processing complete.")
        return frame_contexts