import cv2
import os
import time

class FrameExtractor:
    def __init__(self, output_dir="frames"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract(self, video_path, interval_seconds=2):
        """
        Authentically extracts frames from a video file using OpenCV.
        Returns a list of dictionaries containing frame metadata.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at {video_path}")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * interval_seconds)
        
        extracted_metadata = []
        frame_count = 0
        saved_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval_frames == 0:
                frame_id = saved_count
                filename = f"frame_{frame_id:05d}.jpg"
                filepath = os.path.join(self.output_dir, filename)
                
                # Save the real image to disk
                cv2.imwrite(filepath, frame)
                
                extracted_metadata.append({
                    "frame_id": frame_id,
                    "image_path": filepath
                })
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        return extracted_metadata