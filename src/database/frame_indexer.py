import sqlite3
import json
import os

class FrameIndexer:
    def __init__(self, db_path="data/sentinel.db"):
        self.db_path = db_path
        self._ensure_db_and_tables()

    def _ensure_db_and_tables(self):
        """Self-healing mechanism to ensure tables exist before the real Gemini data arrives."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create Frame Index Table for Authentic Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS frame_index (
                frame_id INTEGER PRIMARY KEY,
                timestamp TEXT,
                location_name TEXT,
                raw_vlm_description TEXT,
                activity_description TEXT,
                has_people INTEGER,
                has_vehicles INTEGER,
                detected_objects_json TEXT
            )
        ''')
        
        # Create Alerts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                rule_id TEXT,
                frame_id INTEGER,
                timestamp TEXT,
                location_name TEXT,
                severity_level TEXT,
                alert_message TEXT,
                triggered_by TEXT,
                is_resolved INTEGER,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def bulk_index(self, analyzed_contexts):
        """Indexes authentic analysis results from Gemini 2.5 Flash into SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ctx in analyzed_contexts:
            # Safely extract data regardless of whether context is a dictionary or an object
            frame_id = getattr(ctx, 'frame_id', ctx.get('frame_id') if isinstance(ctx, dict) else None)
            
            # Extract telemetry context
            telemetry = getattr(ctx, 'telemetry', ctx.get('telemetry', {}) if isinstance(ctx, dict) else {})
            timestamp = telemetry.get('timestamp', 'Unknown') if isinstance(telemetry, dict) else getattr(telemetry, 'timestamp', 'Unknown')
            location = telemetry.get('location_name', 'Unknown') if isinstance(telemetry, dict) else getattr(telemetry, 'location_name', 'Unknown')
            
            # Extract real Gemini analysis result
            analysis = getattr(ctx, 'analysis_result', ctx.get('analysis_result') if isinstance(ctx, dict) else None)
            
            raw_desc = ""
            act_desc = ""
            has_people = 0
            has_vehicles = 0
            objs_json = "[]"
            
            if analysis:
                raw_desc = getattr(analysis, 'raw_description', analysis.get('raw_description', '') if isinstance(analysis, dict) else '')
                act_desc = getattr(analysis, 'activity_description', analysis.get('activity_description', '') if isinstance(analysis, dict) else '')
                
                # Handle booleans safely
                hp = getattr(analysis, 'has_people', analysis.get('has_people') if isinstance(analysis, dict) else False)
                has_people = 1 if hp else 0
                
                hv = getattr(analysis, 'has_vehicles', analysis.get('has_vehicles') if isinstance(analysis, dict) else False)
                has_vehicles = 1 if hv else 0
                
                # Handle objects list
                objs = getattr(analysis, 'detected_objects', analysis.get('detected_objects', []) if isinstance(analysis, dict) else [])
                objs_json = json.dumps(objs)
            
            if frame_id is not None:
                cursor.execute('''
                    INSERT OR REPLACE INTO frame_index 
                    (frame_id, timestamp, location_name, raw_vlm_description, activity_description, has_people, has_vehicles, detected_objects_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (frame_id, timestamp, location, str(raw_desc), str(act_desc), has_people, has_vehicles, objs_json))
                
        conn.commit()
        conn.close()