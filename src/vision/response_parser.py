import re
import logging
from typing import List
from src.vision.analysis_result import AnalysisResult

logger = logging.getLogger(__name__)

class ResponseParser:
    """
    Parses unstructured VLM text into a structured AnalysisResult object using 
    regex for structural compliance and heuristics for flag extraction.
    """
    
    # Precompiled regex for performance
    OBJECTS_PATTERN = re.compile(r'OBJECTS:\s*(.*?)(?=\nACTIVITY:|\nOBSERVATIONS:|$)', re.IGNORECASE | re.DOTALL)
    ACTIVITY_PATTERN = re.compile(r'ACTIVITY:\s*(.*?)(?=\nOBSERVATIONS:|$)', re.IGNORECASE | re.DOTALL)
    OBS_PATTERN = re.compile(r'OBSERVATIONS:\s*(.*?)$', re.IGNORECASE | re.DOTALL)

    VEHICLE_KEYWORDS = {'truck', 'car', 'vehicle', 'sedan', 'suv', 'van', 'pickup', 'motorcycle', 'f-150', 'f150'}
    PERSON_KEYWORDS = {'person', 'people', 'man', 'woman', 'child', 'individual', 'pedestrian', 'human', 'male', 'female'}
    SUSPICIOUS_KEYWORDS = {'loitering', 'running', 'hiding', 'unauthorized', 'suspicious', 'trespassing', 'dark clothing'}

    @classmethod
    def parse(cls, raw_text: str) -> AnalysisResult:
        """Executes the parsing logic with fallback mechanisms."""
        if not raw_text or raw_text.startswith("ERROR:"):
            return AnalysisResult(raw_description=raw_text)

        result = AnalysisResult(raw_description=raw_text)
        
        # 1. Structural Parsing
        objects_match = cls.OBJECTS_PATTERN.search(raw_text)
        activity_match = cls.ACTIVITY_PATTERN.search(raw_text)
        obs_match = cls.OBS_PATTERN.search(raw_text)
        
        objects_text = objects_match.group(1).strip() if objects_match else ""
        activity_text = activity_match.group(1).strip() if activity_match else ""
        obs_text = obs_match.group(1).strip() if obs_match else ""

        # Fallback if VLM ignores format instructions
        if not objects_text and not activity_text and not obs_text:
            logger.debug("VLM bypassed strict formatting. Falling back to global heuristics.")
            objects_text = raw_text
            activity_text = raw_text

        result.activity_description = activity_text.replace('\n', ' ').strip()

        # 2. Object Extraction
        if objects_text.lower() not in ['none', '', 'n/a']:
            # Split by common delimiters
            raw_objects = re.split(r',|\n|- ', objects_text)
            result.detected_objects = [
                obj.strip() for obj in raw_objects 
                if len(obj.strip()) > 2 and obj.strip().lower() != 'none'
            ]

        # 3. Global Heuristic Flagging
        combined_text = raw_text.lower()

        # Vehicle Evaluation
        if any(kw in combined_text for kw in cls.VEHICLE_KEYWORDS):
            result.has_vehicles = True
            for obj in result.detected_objects:
                if any(kw in obj.lower() for kw in cls.VEHICLE_KEYWORDS):
                    result.vehicle_details.append({"type": "extracted", "description": obj})

        # People Evaluation
        if any(kw in combined_text for kw in cls.PERSON_KEYWORDS):
            result.has_people = True
            # Rough approximation of person count based on keyword frequency in objects text
            words = objects_text.lower().split()
            count = sum(1 for word in words if word in cls.PERSON_KEYWORDS)
            result.person_count = count if count > 0 else 1
            
            # Catch multiple people markers
            if "group" in combined_text or "two" in combined_text or "multiple" in combined_text:
                result.person_count = max(result.person_count, 2)

        # Suspicious Activity Evaluation
        if any(kw in combined_text for kw in cls.SUSPICIOUS_KEYWORDS):
            result.is_suspicious = True

        return result