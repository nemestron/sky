import os
import time
import logging
from typing import Optional
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

from src.vision.prompts import VLM_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client for interacting with the Google Gemini 2.5 Flash API.
    Handles authentication, rate limiting, and retry logic.
    """
    
    def __init__(self, rpm_limit: int = 14):
        """
        Initializes the Gemini client.
        Free tier allows 15 RPM, setting default to 14 to maintain a safe buffer.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        genai.configure(api_key=api_key)

        # Initialize the model with the system instruction and generation config
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=VLM_SYSTEM_PROMPT,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for factual consistency
                max_output_tokens=1024,
            )
        )

        self.rpm_limit = rpm_limit
        self.min_request_interval = 60.0 / self.rpm_limit
        self.last_request_time = 0.0

    def _handle_rate_limiting(self) -> None:
        """Enforces the requests-per-minute limit by sleeping if necessary."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    def send_frame_for_analysis(self, image: Image.Image, context_prompt: Optional[str] = "") -> str:
        """
        Sends an image frame and optional context to the Gemini API for analysis.
        Implements exponential backoff for transient errors.
        """
        max_retries = 3
        base_delay = 2.0

        for attempt in range(max_retries):
            try:
                self._handle_rate_limiting()
                
                contents = [image]
                if context_prompt:
                    contents.append(context_prompt)
                    
                response = self.model.generate_content(contents)
                return response.text
                
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached. Returning fallback error response.")
                    return "ERROR: VLM analysis failed."