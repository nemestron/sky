from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
FRAMES_DIR = BASE_DIR / "frames"
SRC_DIR = BASE_DIR / "src"

# Video Configuration
SAMPLE_VIDEO_PATH = DATA_DIR / "sample_surveillance.mp4"

# Frame Extraction Settings
TARGET_IMAGE_WIDTH = 1280
TARGET_IMAGE_HEIGHT = 720
# Explicitly aligned to the physical limit of the sample video (189 frames)
EXPECTED_FRAME_COUNT = 189