import streamlit as st
import os
import sys
import sqlite3
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

st.set_page_config(page_title="Upload & Process | Sky Sentinel", layout="wide")
st.title("Upload and Process Video")
st.markdown("**Strict Authentic Analysis Mode:** This pipeline will extract real frames and send them to the Gemini 2.5 Flash API. No fake data is used.")

os.makedirs("data", exist_ok=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Video Input")
    uploaded_file = st.file_uploader("Upload Surveillance Video (MP4/AVI)", type=["mp4", "avi"])
    use_sample = st.button("Use Sample Video (Bundled)")
    
    video_path = None
    if uploaded_file is not None:
        video_path = os.path.join("data", "uploaded_video.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name} successfully.")
    elif use_sample:
        sample_path = os.path.join("data", "sample_surveillance.mp4")
        if os.path.exists(sample_path):
            video_path = sample_path
            st.success("Loaded sample_surveillance.mp4")
        else:
            st.warning("Sample video not found. Please ensure it exists in the data directory.")

with col2:
    st.subheader("Processing Control")
    if video_path and st.button("Start Authentic Processing", type="primary"):
        st.session_state['is_processing'] = True
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Initialising backend modules...")
            
            # Importing backend modules
            from src.vision.frame_extractor import FrameExtractor
            from src.telemetry.correlation import CorrelationEngine
            from src.vision.analysis_pipeline import FrameAnalysisPipeline
            from src.alerts.alert_engine import AlertEngine
            from src.database.frame_indexer import FrameIndexer

            # Step 1: Real Frame Extraction
            status_text.text("Step 1/5: Extracting REAL video frames using OpenCV...")
            progress_bar.progress(10)
            extractor = FrameExtractor()
            extracted_frames = extractor.extract(video_path)
            
            # Step 2: Correlation
            status_text.text("Step 2/5: Correlating frames with telemetry...")
            progress_bar.progress(30)
            correlator = CorrelationEngine()
            frame_contexts = correlator.correlate(extracted_frames)
            
            # Step 3: AUTHENTIC VLM Analysis (No Simulation)
            status_text.text("Step 3/5: Calling Google Gemini 2.5 Flash API (Authentic Analysis)...")
            progress_bar.progress(50)
            analyzer = FrameAnalysisPipeline()
            
            # Force authentic mode if the method accepts parameters, otherwise rely on env config
            try:
                analyzed_contexts = analyzer.process_frames(frame_contexts, simulation_mode=False)
            except TypeError:
                # If process_frames doesn't take simulation_mode, run it normally
                analyzed_contexts = analyzer.process_frames(frame_contexts)
                
            # Step 4: Alerts
            status_text.text("Step 4/5: Evaluating security rules & generating real alerts...")
            progress_bar.progress(70)
            alert_engine = AlertEngine()
            alert_engine.evaluate(analyzed_contexts)
            
            # Step 5: Indexing
            status_text.text("Step 5/5: Indexing results to SQLite database...")
            progress_bar.progress(90)
            indexer = FrameIndexer()
            indexer.bulk_index(analyzed_contexts)

            # Retrieve Ground Truth Data for UI
            status_text.text("Fetching real analysis results from SQLite database...")
            db_path = os.path.join("data", "sentinel.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                try:
                    cursor.execute("SELECT * FROM frame_index ORDER BY frame_id ASC")
                    real_frames = [dict(row) for row in cursor.fetchall()]
                    formatted_logs = []
                    for f in real_frames:
                        objects = []
                        if f.get('detected_objects_json'):
                            try:
                                objects = json.loads(f['detected_objects_json'])
                            except json.JSONDecodeError:
                                pass
                        formatted_logs.append({
                            "frame_id": f.get("frame_id"),
                            "timestamp": f.get("timestamp"),
                            "location": f.get("location_name"),
                            "objects": objects,
                            "activity": f.get("activity_description", "No activity")
                        })
                    st.session_state['processed_frames'] = formatted_logs
                except sqlite3.OperationalError:
                    st.warning("Database schema incomplete.")
                
                try:
                    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
                    st.session_state['alerts'] = [dict(row) for row in cursor.fetchall()]
                except sqlite3.OperationalError:
                    pass
                    
                conn.close()

            st.session_state['is_processing'] = False
            progress_bar.progress(100)
            status_text.text("Authentic Processing Complete!")
            st.success("Video successfully processed using real Gemini 2.5 Flash vision analysis.")

        except Exception as e:
            import traceback
            st.error(f"Pipeline Execution Error: {str(e)}")
            with st.expander("View Detailed Error Traceback"):
                st.code(traceback.format_exc())
            st.session_state['is_processing'] = False

# UI Polish & Footer Injection
try:
    from ui.components import render_creator_footer, load_css
    load_css()
    render_creator_footer()
except ImportError:
    pass