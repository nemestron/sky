import cv2
import sys
from pathlib import Path
from PIL import Image

# Add root src directory to Python path to allow absolute imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import (
    SAMPLE_VIDEO_PATH, 
    FRAMES_DIR, 
    TARGET_IMAGE_WIDTH, 
    TARGET_IMAGE_HEIGHT, 
    EXPECTED_FRAME_COUNT
)

class FrameExtractor:
    def __init__(self, video_path=SAMPLE_VIDEO_PATH, output_dir=FRAMES_DIR):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_frames(self, target_count=EXPECTED_FRAME_COUNT):
        """
        Extracts a specific number of frames evenly spaced across the video duration.
        Resizes them and saves them to the frames directory.
        """
        if not self.video_path.exists():
            print(f"Warning: Video file not found at {self.video_path}")
            return None

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return None

        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_video_frames == 0:
            print("Error: Video has 0 frames.")
            return None

        # Calculate the step size to evenly sample the target number of frames
        step = max(1, total_video_frames // target_count)
        
        extracted_count = 0
        extracted_frame_ids = []
        
        print(f"Starting extraction. Video has {total_video_frames} frames at {original_fps:.2f} FPS.")
        print(f"Targeting {target_count} frames. Extracting roughly every {step}th frame.")

        current_video_frame = 0
        
        while extracted_count < target_count and current_video_frame < total_video_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_video_frame)
            ret, frame = cap.read()
            
            if not ret:
                break
                
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            pil_image = pil_image.resize((TARGET_IMAGE_WIDTH, TARGET_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
            
            frame_filename = f"frame_{extracted_count:05d}.jpg"
            output_path = self.output_dir / frame_filename
            
            pil_image.save(output_path, "JPEG", quality=85)
            extracted_frame_ids.append(extracted_count)
            extracted_count += 1
            current_video_frame += step

        cap.release()
        
        result = {
            "total_video_frames": total_video_frames,
            "original_fps": original_fps,
            "extracted_count": extracted_count,
            "extracted_frame_ids": extracted_frame_ids,
            "output_dir": str(self.output_dir)
        }
        
        print(f"Extraction complete. Saved {extracted_count} frames to {self.output_dir}")
        return result

if __name__ == "__main__":
    extractor = FrameExtractor()
    extractor.extract_frames()