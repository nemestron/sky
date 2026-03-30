import os
import json
import sqlite3
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoSummariser:
    def __init__(self):
        """
        Initializes the VideoSummariser, setting up file paths and the LLM connection.
        """
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(self.base_path, 'data', 'sentinel.db')
        self.json_path = os.path.join(self.base_path, 'data', 'session_summary.json')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Summarisation will fail.")
            self.llm = None
        else:
            # Low temperature for factual, grounded reporting
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=api_key)

    def _gather_statistics(self) -> dict:
        """
        Aggregates key metrics from the SQLite database to provide context for the LLM.
        """
        stats = {
            "total_frames": 0,
            "total_people_detections": 0,
            "total_vehicles": 0,
            "alerts_by_severity": {},
            "top_locations": []
        }
        
        if not os.path.exists(self.db_path):
            return stats

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic safeguards to ensure tables exist before querying
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='frame_index'")
                if not cursor.fetchone():
                    return stats

                cursor.execute("SELECT COUNT(*) FROM frame_index")
                stats["total_frames"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM frame_index WHERE has_people = 1")
                stats["total_people_detections"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM detected_objects WHERE object_type LIKE '%vehicle%' OR object_type LIKE '%car%' OR object_type LIKE '%truck%'")
                stats["total_vehicles"] = cursor.fetchone()[0]

                # Aggregate alerts if the alerts table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
                if cursor.fetchone():
                    cursor.execute("SELECT severity_level, COUNT(*) FROM alerts GROUP BY severity_level")
                    for row in cursor.fetchall():
                        stats["alerts_by_severity"][row[0]] = row[1]

                # Find the most active locations
                cursor.execute("SELECT location_name, COUNT(*) FROM frame_index GROUP BY location_name ORDER BY COUNT(*) DESC LIMIT 3")
                stats["top_locations"] = [f"{row[0]} ({row[1]} frames)" for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error gathering statistics from database: {str(e)}")
        
        return stats

    def _save_summary(self, summary_text: str, stats: dict):
        """
        Persists the generated summary and statistics to both a JSON file and the SQLite database.
        """
        output_data = {
            "summary": summary_text,
            "statistics": stats
        }
        
        # Save to JSON for fast UI loading
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4)
            logger.info(f"Session summary saved to {self.json_path}")
        except Exception as e:
            logger.error(f"Error saving summary to JSON: {str(e)}")

        # Save to SQLite database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS summary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        summary_text TEXT,
                        stats_json TEXT
                    )
                ''')
                cursor.execute(
                    "INSERT INTO summary (summary_text, stats_json) VALUES (?, ?)",
                    (summary_text, json.dumps(stats))
                )
                conn.commit()
                logger.info("Session summary saved to SQLite database.")
        except Exception as e:
            logger.error(f"Error saving summary to SQLite: {str(e)}")

    def generate_summary(self) -> str:
        """
        Main method to aggregate data, prompt the LLM, and generate the final report.
        """
        if not self.llm:
            return "Error: LLM not configured. Check API key."
            
        stats = self._gather_statistics()
        
        if stats["total_frames"] == 0:
            return "No surveillance data available in the database to summarize."

        prompt_template = """
You are a professional security analyst writing an end-of-shift report.
Based on the following aggregated database statistics from a 24-hour drone surveillance session, write a concise paragraph (2-4 sentences) summarizing the events.

STATISTICS:
Total Frames Processed: {total_frames}
Total People Detections: {total_people_detections}
Total Vehicle Detections: {total_vehicles}
Alerts by Severity: {alerts_by_severity}
Most Active Locations: {top_locations}

INSTRUCTIONS:
- Write in a professional, factual security report style.
- Keep it to 2-4 sentences.
- Do not hallucinate or add information that is not in the statistics.
- If there are no alerts or significant events, explicitly state that activity was within normal parameters.
"""
        prompt = PromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format(
            total_frames=stats.get("total_frames", 0),
            total_people_detections=stats.get("total_people_detections", 0),
            total_vehicles=stats.get("total_vehicles", 0),
            alerts_by_severity=stats.get("alerts_by_severity", "None"),
            top_locations=", ".join(stats.get("top_locations", []))
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            summary_text = response.content.strip()
            self._save_summary(summary_text, stats)
            return summary_text
        except Exception as e:
            logger.error(f"Error generating summary via LLM: {str(e)}")
            return "System Error: Failed to generate summary due to an internal processing error."

# Creator: Dhiraj Malwade